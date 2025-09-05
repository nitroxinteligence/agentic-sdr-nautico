"""
Calendar Service - Google Calendar API com OAuth 2.0
Funcionalidades habilitadas: Google Meet + Participantes + Convites
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta, time
import asyncio
import uuid
import random
from googleapiclient.errors import HttpError
from app.utils.logger import emoji_logger
from app.config import settings
from app.integrations.google_oauth_handler import get_oauth_handler
from app.integrations.redis_client import redis_client

from app.decorators.error_handler import async_handle_errors


class CalendarServiceReal:
    """
    Serviço REAL de calendário - Google Calendar API com OAuth 2.0
    """

    def __init__(self):
        self.is_initialized = False
        self.calendar_id = settings.google_calendar_id
        self.service = None
        self.oauth_handler = get_oauth_handler()
        self.business_hours = {
            "start_hour": 8,
            "end_hour": 18,
            "weekdays": [0, 1, 2, 3, 4]
        }
        self.lock_timeout = 30

    @async_handle_errors(retry_policy='google_calendar')
    async def initialize(self):
        """Inicializa conexão REAL com Google Calendar usando OAuth 2.0."""
        if self.is_initialized:
            return
            
        # Verificar se Google Calendar está habilitado
        if not settings.enable_google_calendar:
            emoji_logger.system_warning("Google Calendar desabilitado - pulando inicialização")
            return
            
        try:
            if not self.calendar_id:
                emoji_logger.system_warning("GOOGLE_CALENDAR_ID não configurado - Google Calendar desabilitado")
                return

            self.service = self.oauth_handler.build_calendar_service()
            if not self.service:
                emoji_logger.service_error("Não foi possível construir o serviço do Google Calendar. Verifique a autorização OAuth.")
                return

            # Verifica se o calendário existe
            calendar = await asyncio.to_thread(
                self.service.calendars().get(calendarId=self.calendar_id).execute
            )
            
            summary = calendar.get('summary', self.calendar_id)
            emoji_logger.service_ready(
                f"Google Calendar conectado via OAuth ao calendário: '{summary}'",
                calendar_id=self.calendar_id
            )
            self.is_initialized = True

        except HttpError as e:
            if e.resp.status == 404:
                emoji_logger.service_error(
                    f"O calendário com ID '{self.calendar_id}' não foi encontrado. "
                    "Verifique se o GOOGLE_CALENDAR_ID no arquivo .env está correto e se a conta de serviço tem permissão."
                )
            else:
                emoji_logger.service_error(f"Ocorreu um erro na API do Google: {e}")
            self.is_initialized = False
        except ValueError as e:
            emoji_logger.service_error(str(e))
            self.is_initialized = False
        except Exception as e:
            emoji_logger.service_error(f"Erro inesperado ao inicializar o CalendarService: {e}")
            self.is_initialized = False

    def is_business_hours(self, datetime_obj: datetime) -> bool:
        """Verifica se a data/hora está dentro do horário comercial"""
        if datetime_obj.weekday() not in self.business_hours["weekdays"]:
            return False
        if not (self.business_hours["start_hour"] <=
                datetime_obj.hour < self.business_hours["end_hour"]):
            return False
        return True

    def get_next_business_day(self, date: datetime) -> datetime:
        """Retorna o próximo dia útil disponível"""
        next_day = date
        while next_day.weekday() not in self.business_hours["weekdays"]:
            next_day += timedelta(days=1)
        return next_day

    def format_business_hours_message(self) -> str:
        """Retorna mensagem formatada sobre horário comercial"""
        weekday_names = {
            0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta"
        }
        days_str = (
            f"{weekday_names[self.business_hours['weekdays'][0]]} a "
            f"{weekday_names[self.business_hours['weekdays'][-1]]}"
        )
        return (
            f"{days_str}, das {self.business_hours['start_hour']}h às "
            f"{self.business_hours['end_hour']}h"
        )

    async def _acquire_lock(self, lock_key: str) -> bool:
        """Adquire um lock distribuído usando Redis"""
        try:
            lock_value = str(uuid.uuid4())
            result = await redis_client.redis_client.set(
                f"calendar_lock:{lock_key}",
                lock_value,
                nx=True,
                ex=self.lock_timeout
            )
            if result:
                self._lock_value = lock_value
                self._lock_key = lock_key
                return True
            return False
        except Exception as e:
            emoji_logger.service_error(f"Erro ao adquirir lock: {e}")
            return False

    async def _release_lock(self) -> bool:
        """Libera o lock distribuído"""
        try:
            if not hasattr(self, '_lock_key') or not hasattr(self, '_lock_value'):
                return False
            lock_key = f"calendar_lock:{self._lock_key}"
            lock_value = self._lock_value
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            # A chamada correta para eval é posicional: script, num_keys, key, arg
            result = await redis_client.redis_client.eval(
                lua_script, 1, lock_key, lock_value
            )
            if hasattr(self, '_lock_key'):
                delattr(self, '_lock_key')
            if hasattr(self, '_lock_value'):
                delattr(self, '_lock_value')
            return result == 1
        except Exception as e:
            emoji_logger.service_error(f"Erro ao liberar lock: {e}")
            return False

    async def _schedule_meeting_with_retry(
            self, event_data: Dict[str, Any], max_retries: int = 3
    ) -> Dict[str, Any]:
        """Agenda reunião com retry em caso de conflitos"""
        import random
        for attempt in range(max_retries):
            try:
                created_event = await asyncio.to_thread(
                    self.service.events().insert(
                        calendarId=self.calendar_id,
                        body=event_data,
                        conferenceDataVersion=1,
                        sendUpdates='all' if event_data.get('attendees') else 'none'
                    ).execute
                )
                return created_event
            except HttpError as e:
                if e.resp.status == 409 and attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    emoji_logger.service_warning(
                        f"⚠️ Conflito de horário, tentando novamente em "
                        f"{delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    raise e
        raise Exception("Número máximo de tentativas excedido")

    async def _is_slot_available(self, start_time: datetime, end_time: datetime, event_id_to_ignore: Optional[str] = None) -> bool:
        """Verifica internamente se um slot de horário está livre."""
        emoji_logger.calendar_event(f"Verificando disponibilidade interna para {start_time.strftime('%Y-%m-%d %H:%M')}...")
        
        time_min = start_time.isoformat()
        time_max = end_time.isoformat()

        try:
            events_result = await asyncio.to_thread(
                self.service.events().list(
                    calendarId=self.calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True
                ).execute
            )
            
            conflicting_events = [
                event for event in events_result.get('items', [])
                if event.get('id') != event_id_to_ignore
            ]

            if conflicting_events:
                emoji_logger.service_warning(f"Conflito de agendamento detectado para o horário {start_time.strftime('%H:%M')}.")
                return False
            
            emoji_logger.system_success(f"Horário {start_time.strftime('%H:%M')} está livre.")
            return True
        except Exception as e:
            emoji_logger.service_error(f"Erro ao verificar disponibilidade interna: {e}")
            # Em caso de erro na verificação, é mais seguro assumir que não está disponível para evitar double booking.
            return False

    @async_handle_errors(retry_policy='google_calendar')
    async def check_availability(self, date_request: str) -> Dict[str, Any]:
        """Verifica disponibilidade REAL no Google Calendar, respeitando o horário comercial."""
        if not self.is_initialized:
            await self.initialize()
        
        lock_key = "calendar:availability_check"
        if not await redis_client.acquire_lock(lock_key, ttl=10):
            return {"success": False, "error": "lock_not_acquired", "message": "Sistema ocupado, tente novamente."}
        
        try:
            target_day = None
            if date_request:
                try:
                    target_day = datetime.strptime(date_request, "%Y-%m-%d").date()
                except ValueError:
                    emoji_logger.service_warning(f"Formato de data inválido: {date_request}. Usando fallback.")
                    target_day = (datetime.now() + timedelta(days=1)).date()
            else:
                target_day = (datetime.now() + timedelta(days=1)).date()

            # Validação de dia útil
            if target_day.weekday() not in self.business_hours["weekdays"]:
                next_business_day = self.get_next_business_day(datetime.combine(target_day, datetime.min.time()))
                return {
                    "success": True,
                    "available_slots": [],
                    "date": target_day.strftime("%Y-%m-%d"),
                    "message": f"Não há horários disponíveis em {target_day.strftime('%d/%m')}, pois é fim de semana. Que tal na {next_business_day.strftime('%A, %d/%m')}?"
                }

            time_min = datetime.combine(target_day, datetime.min.time()).isoformat() + 'Z'
            time_max = datetime.combine(target_day, datetime.max.time()).isoformat() + 'Z'
            
            events_result = await asyncio.to_thread(
                self.service.events().list(
                    calendarId=self.calendar_id, timeMin=time_min,
                    timeMax=time_max, singleEvents=True, orderBy='startTime'
                ).execute
            )
            events = events_result.get('items', [])
            
            all_slots = []
            for hour in range(self.business_hours["start_hour"], self.business_hours["end_hour"]):
                slot_start = datetime.combine(target_day, time(hour=hour))
                if not self.is_business_hours(slot_start):
                    continue

                slot_end = slot_start + timedelta(hours=1)
                is_free = all(
                    slot_end <= datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00')).replace(tzinfo=None) or
                    slot_start >= datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00')).replace(tzinfo=None)
                    for event in events if 'dateTime' in event.get('start', {})
                )
                if is_free:
                    all_slots.append(f"{hour:02d}:00")

            return {
                "success": True,
                "date": target_day.strftime("%Y-%m-%d"),
                "available_slots": all_slots,
                "message": f"Horários disponíveis para {target_day.strftime('%d/%m')}: {', '.join(all_slots) if all_slots else 'Nenhum'}",
                "real": True
            }
        except Exception as e:
            emoji_logger.service_error(f"Erro ao verificar disponibilidade: {e}")
            return {"success": False, "message": f"Erro ao verificar disponibilidade: {e}"}
        finally:
            await redis_client.release_lock(lock_key)

    @async_handle_errors(retry_policy='google_calendar')
    async def schedule_meeting(
            self, date: str, time: str, lead_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Agenda reunião REAL no Google Calendar com validação robusta de data e horário."""
        if not self.is_initialized:
            await self.initialize()

        try:
            # Etapa 1: Parse e validação da data
            now = datetime.now()
            date_str = date.lower().strip()
            
            if date_str == 'amanha' or date_str == 'amanhã':
                target_date = (now + timedelta(days=1)).date()
            elif date_str == 'hoje':
                target_date = now.date()
            else:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            meeting_time = datetime.strptime(time, "%H:%M").time()
            meeting_datetime = datetime.combine(target_date, meeting_time)
            meeting_end = meeting_datetime + timedelta(hours=1)

            # Etapa 2: Validação de dia e horário comercial
            if not self.is_business_hours(meeting_datetime):
                next_business_day = self.get_next_business_day(meeting_datetime)
                return {
                    "success": False, 
                    "error": "outside_business_hours",
                    "message": f"O horário solicitado ({target_date.strftime('%d/%m')} às {time}) está fora do nosso expediente. Por favor, escolha um horário de Segunda a Sexta, entre 8h e 18h. O próximo dia útil é {next_business_day.strftime('%A, %d/%m')}."
                }

        except ValueError:
            return {"success": False, "message": f"Formato de data ou hora inválido. Use 'YYYY-MM-DD' para data e 'HH:MM' para hora."}

        # Etapa 3: Verificação proativa de disponibilidade
        import pytz
        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        aware_meeting_datetime = sao_paulo_tz.localize(meeting_datetime)
        aware_meeting_end = sao_paulo_tz.localize(meeting_end)

        if not await self._is_slot_available(aware_meeting_datetime, aware_meeting_end):
            availability_result = await self.check_availability(target_date.strftime('%Y-%m-%d'))
            return {
                "success": False, "error": "conflict",
                "message": f"O horário {time} no dia {target_date.strftime('%d/%m')} já está ocupado.",
                "available_slots": availability_result.get("available_slots", []),
                "date": availability_result.get("date")
            }

        lock_key = f"calendar:schedule:{target_date.strftime('%Y-%m-%d')}:{time}"
        if not await redis_client.acquire_lock(lock_key, ttl=30):
            return {"success": False, "error": "lock_not_acquired", "message": "Este horário acabou de ser agendado por outra pessoa. Por favor, escolha outro."}

        try:
            description_template = """⚪🔴 REUNIÃO NÁUTICO - PROGRAMA DE SÓCIOS

Olá {lead_name}!

É com grande satisfação que confirmamos nossa reunião para apresentar como você pode fazer parte da família alvirrubra como sócio do Clube Náutico Capibaribe.

Somos o clube mais tradicional de Pernambuco, com mais de 120 anos de história e milhares de torcedores apaixonados. Nossa missão é fortalecer o Timão e oferecer aos sócios os melhores benefícios e experiências alvirrubrAS.

✅ O QUE VAMOS APRESENTAR:
• Análise personalizada do seu perfil de torcedor
• Apresentação dos nossos 4 planos de sócio
• Sócio Contribuinte - benefícios básicos e desconto em jogos
• Sócio Patrimonial - acesso a áreas VIP e eventos exclusivos
• Sócio Remido - prioridade total e benefícios vitalícios
• Sócio Benemérito - status máximo e reconhecimento especial

✅ NOSSOS DIFERENCIAIS:
• Mais de 300 estabelecimentos parceiros com descontos
• Acesso prioritário a ingressos em todos os jogos
• Produtos oficiais com preços especiais
• Programa Sócio Mais Fiel do Nordeste

Agradecemos pela paixão alvirrubra e pelo interesse em fazer parte da nossa família. Nossa equipe está ansiosa para mostrar como você pode viver intensamente sua paixão pelo Timão sendo sócio do Náutico.

✨ Desejamos uma excelente reunião e estamos confiantes de que será o início de uma parceria de sucesso!

Atenciosamente,
Equipe Náutico
⚪🔴 Timbu Eterno!"""

            event_description = description_template.format(lead_name=lead_info.get("name", "Cliente"))

            event = {
                'summary': f'⚪🔴 Reunião Náutico com {lead_info.get("name", "Torcedor")}',
                'description': event_description,
                'start': {'dateTime': aware_meeting_datetime.isoformat(), 'timeZone': 'America/Sao_Paulo'},
                'end': {'dateTime': aware_meeting_end.isoformat(), 'timeZone': 'America/Sao_Paulo'},
                'conferenceData': {'createRequest': {'requestId': f'meet-{uuid.uuid4()}', 'conferenceSolutionKey': {'type': 'hangoutsMeet'}}},
                'attendees': [{'email': email} for email in set([lead_info.get("email")] + lead_info.get("attendees", [])) if email],
                'reminders': {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 60}, {'method': 'popup', 'minutes': 15}]}
            }
            
            created_event = await self._schedule_meeting_with_retry(event)
            meet_link = next((ep['uri'] for ep in created_event.get('conferenceData', {}).get('entryPoints', []) if ep.get('entryPointType') == 'video'), None)
            
            return {
                "success": True, "meeting_id": created_event.get('id'),
                "google_event_id": created_event.get('id'),
                "start_time": created_event.get('start', {}).get('dateTime'),
                "date": target_date.strftime('%Y-%m-%d'), "time": time,
                "link": created_event.get('htmlLink'), "meet_link": meet_link,
                "attendees": [att['email'] for att in event['attendees']],
                "message": f"✅ Reunião confirmada para {target_date.strftime('%d/%m')} às {time}.", "real": True
            }
        except Exception as e:
            return {"success": False, "message": f"Erro ao agendar: {e}"}
        finally:
            await redis_client.release_lock(lock_key)

    @async_handle_errors(retry_policy='google_calendar')
    async def cancel_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Cancela reunião REAL no Google Calendar"""
        if not self.is_initialized:
            await self.initialize()
        lock_key = f"cancel:{meeting_id}"
        if not await self._acquire_lock(lock_key):
            return {
                "success": False, "error": "lock_not_acquired",
                "message": "Sistema ocupado."
            }
        try:
            await asyncio.to_thread(
                self.service.events().delete(
                    calendarId=self.calendar_id, eventId=meeting_id
                ).execute
            )
            return {
                "success": True, "message": "Reunião cancelada.",
                "meeting_id": meeting_id, "real": True
            }
        except HttpError as e:
            if e.resp.status == 404:
                return {"success": True, "message": "Evento já cancelado."}
            raise
        finally:
            await self._release_lock()

    @async_handle_errors(retry_policy='google_calendar')
    async def reschedule_meeting(
        self, date: Optional[str], time: Optional[str], lead_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Reagenda a última reunião de um lead, buscando-a no Supabase."""
        if not self.is_initialized:
            await self.initialize()

        from app.integrations.supabase_client import supabase_client
        
        lead_id = lead_info.get("id")
        if not lead_id:
            return {"success": False, "message": "ID do lead não encontrado para reagendamento."}

        emoji_logger.calendar_event(f"Iniciando reagendamento para o lead: {lead_id}")

        try:
            # Passo 1: Buscar a última qualificação (reunião) do lead no Supabase
            latest_qualification = await supabase_client.get_latest_qualification(lead_id)
            if not latest_qualification or not latest_qualification.get("google_event_id"):
                return {"success": False, "message": "Nenhuma reunião ativa encontrada para reagendar."}
            
            meeting_id = latest_qualification["google_event_id"]
            emoji_logger.calendar_event(f"Reunião encontrada para reagendamento: {meeting_id}")

            # Passo 2: Obter detalhes do evento original do Google Calendar
            original_event = await self.get_event(meeting_id)
            if not original_event:
                return {"success": False, "message": f"Reunião com ID {meeting_id} não encontrada no Google Calendar."}
            
            original_start_str = original_event.get("start", {}).get("dateTime")
            original_datetime = datetime.fromisoformat(original_start_str)
            
            # Passo 3: Definir a nova data/hora, usando os dados originais como fallback
            new_date = date or original_datetime.strftime("%Y-%m-%d")
            new_time = time or original_datetime.strftime("%H:%M")

            if not date and not time:
                 return {"success": False, "message": "É necessário fornecer uma nova data ou um novo horário para o reagendamento."}

            import pytz
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
            naive_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
            new_datetime = sao_paulo_tz.localize(naive_datetime)
            new_datetime_end = new_datetime + timedelta(hours=1)

            # Passo 4: Verificar disponibilidade do novo horário
            if not await self._is_slot_available(new_datetime, new_datetime_end, event_id_to_ignore=meeting_id):
                suggested_times = await self.check_availability(new_date)
                return {
                    "success": False, "error": "conflict",
                    "message": f"O horário {new_time} de {new_date} já está ocupado. Que tal um destes?",
                    "available_slots": suggested_times.get("available_slots", []),
                    "date": suggested_times.get("date")
                }

            # Passo 5: Atualizar o evento no Google Calendar, incluindo o timezone
            emoji_logger.calendar_event(f"Horário disponível. Atualizando evento {meeting_id}...")
            original_event['start'] = {'dateTime': new_datetime.isoformat(), 'timeZone': 'America/Sao_Paulo'}
            original_event['end'] = {'dateTime': new_datetime_end.isoformat(), 'timeZone': 'America/Sao_Paulo'}

            updated_event = await asyncio.to_thread(
                self.service.events().update(
                    calendarId=self.calendar_id, eventId=meeting_id,
                    body=original_event, sendUpdates='all'
                ).execute
            )
            
            emoji_logger.system_success(f"Reunião {meeting_id} reagendada para {new_date} às {new_time}.")
            meet_link = updated_event.get('hangoutLink')

            # Passo 6: Atualizar o registro de qualificação no Supabase
            await supabase_client.update_lead_qualification(
                latest_qualification['id'],
                {"meeting_scheduled_at": new_datetime.isoformat()}
            )
            emoji_logger.system_info(f"Qualificação {latest_qualification['id']} atualizada no Supabase.")

            return {
                "success": True, "meeting_id": updated_event.get('id'),
                "google_event_id": updated_event.get('id'),
                "start_time": updated_event.get('start', {}).get('dateTime'),
                "date": new_date, "time": new_time,
                "link": updated_event.get('htmlLink'), "meet_link": meet_link,
                "message": f"✅ Reunião reagendada com sucesso para {new_date} às {new_time}."
            }

        except HttpError as e:
            emoji_logger.service_error(f"Erro de API do Google ao reagendar: {e}")
            return {"success": False, "message": f"Erro de API ao reagendar: {e.reason}"}
        except Exception as e:
            emoji_logger.service_error(f"Erro inesperado ao reagendar: {e}")
            return {"success": False, "message": "Ocorreu um erro inesperado durante o reagendamento."}

    @async_handle_errors(retry_policy='google_calendar')
    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Busca um evento específico no Google Calendar pelo ID."""
        if not self.is_initialized:
            await self.initialize()
        try:
            return await asyncio.to_thread(
                self.service.events().get(
                    calendarId=self.calendar_id, eventId=event_id
                ).execute
            )
        except HttpError as e:
            if e.resp.status == 404:
                return None
            raise

    async def health_check(self) -> bool:
        """Verifica saúde do serviço"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            calendar_info = await asyncio.to_thread(
                self.service.calendars().get(calendarId=self.calendar_id).execute
            )
            return calendar_info is not None
        except Exception:
            return False

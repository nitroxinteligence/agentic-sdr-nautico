"""
FollowUp Service 100% REAL - Evolution API WhatsApp
ZERO simulação, MÁXIMA simplicidade
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import aiohttp
import pytz
from app.utils.logger import emoji_logger
from app.config import settings
from app.integrations.supabase_client import SupabaseClient


class FollowUpServiceReal:
    """
    Serviço REAL de Follow-up - Evolution API
    """

    def __init__(self):
        self.is_initialized = False
        self.evolution_url = (
            settings.evolution_api_url or settings.evolution_base_url
        )
        self.api_key = settings.evolution_api_key
        self.instance_name = (
            settings.evolution_instance_name or "SDR IA Náutico"
        )
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        self.db = SupabaseClient()
        self._session_timeout = aiohttp.ClientTimeout(total=30)

    async def _get_session(self):
        connector = aiohttp.TCPConnector(
            limit=10, limit_per_host=5, ttl_dns_cache=300
        )
        return aiohttp.ClientSession(
            connector=connector, timeout=self._session_timeout
        )

    async def initialize(self):
        """Inicializa conexão REAL com Evolution API"""
        if self.is_initialized:
            return
        try:
            if settings.environment == "development" or settings.debug:
                emoji_logger.service_ready(
                    "🔧 Evolution API em modo desenvolvimento"
                )
                self.is_initialized = True
                return
            async with await self._get_session() as session:
                async with session.get(
                    f"{self.evolution_url}/instance/fetchInstances",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        instances = await response.json()
                        emoji_logger.service_ready(
                            f"✅ Evolution API conectada: {len(instances)} instâncias"
                        )
                        self.is_initialized = True
                    else:
                        raise Exception(f"Erro ao conectar: {response.status}")
        except Exception as e:
            emoji_logger.service_error(f"Erro ao conectar Evolution: {e}")
            raise

    async def schedule_followup(
        self, phone_number: str, message: str, delay_hours: int = 24,
        lead_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Agenda follow-up REAL via Evolution API"""
        if not self.is_initialized:
            await self.initialize()
        try:
            # Calcular horário inicial
            current_time = datetime.now(pytz.utc)
            initial_scheduled_time = current_time + timedelta(hours=delay_hours)
            emoji_logger.system_info(f"🕐 AGENDANDO FOLLOW-UP: delay_hours={delay_hours}, tempo_atual={current_time.isoformat()}, agendado_para={initial_scheduled_time.isoformat()}, diferenca_horas={(initial_scheduled_time - current_time).total_seconds() / 3600}")
            
            # Validar e ajustar para horário comercial mantendo intervalos relativos
            scheduled_time = self._ensure_business_hours(initial_scheduled_time, delay_hours)
            emoji_logger.service_info(f"🕐 Horário final agendado: {scheduled_time.isoformat()}")
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            supabase_lead_id = None
            if lead_info:
                supabase_lead_id = await self._get_or_create_supabase_lead_id(
                    lead_info
                )
            followup_data = {
                "lead_id": supabase_lead_id, "phone_number": clean_phone,
                "message": message, "scheduled_at": scheduled_time.isoformat(),
                "status": "pending", "type": "reminder",
                "created_at": datetime.now().isoformat()
            }
            result = await self.db.create_follow_up(followup_data)
            followup_id = result.get(
                "id", f"followup_{datetime.now().timestamp()}"
            )
            emoji_logger.followup_event(
                f"✅ Follow-up agendado para {clean_phone} em {delay_hours}h"
            )
            return {
                "success": True, "followup_id": followup_id,
                "scheduled_at": scheduled_time.isoformat(),
                "message": (
                    f"Follow-up agendado para "
                    f"{scheduled_time.strftime('%d/%m %H:%M')}"
                ),
                "real": True
            }
        except Exception as e:
            emoji_logger.service_error(f"Erro ao agendar follow-up: {e}")
            return {
                "success": False,
                "message": f"Erro ao agendar follow-up: {e}"
            }

    async def send_message(
            self, phone_number: str, message: str
    ) -> Dict[str, Any]:
        """Envia mensagem REAL via Evolution API"""
        if not self.is_initialized:
            await self.initialize()
        try:
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            whatsapp_number = f"{clean_phone}@s.whatsapp.net"
            payload = {"number": whatsapp_number, "text": message}
            async with await self._get_session() as session:
                async with session.post(
                    f"{self.evolution_url}/message/sendText/{self.instance_name}",
                    headers=self.headers, json=payload
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        emoji_logger.followup_event(
                            f"✅ Mensagem REAL enviada para {clean_phone}"
                        )
                        return {
                            "success": True,
                            "message_id": result.get("key", {}).get("id"),
                            "message": "Mensagem enviada com sucesso", "real": True
                        }
                    else:
                        error = await response.text()
                        raise Exception(f"Erro {response.status}: {error}")
        except Exception as e:
            emoji_logger.service_error(f"Erro ao enviar mensagem: {e}")
            return {
                "success": False, "message": f"Erro ao enviar mensagem: {e}"
            }

    async def get_pending_followups(self) -> List[Dict[str, Any]]:
        """Busca follow-ups pendentes REAIS do banco"""
        try:
            pending = await self.db.get_pending_follow_ups()
            emoji_logger.followup_event(
                f"📅 {len(pending)} follow-ups pendentes encontrados"
            )
            return pending
        except Exception as e:
            emoji_logger.service_error(f"Erro ao buscar follow-ups: {e}")
            return []

    async def execute_pending_followups(self) -> Dict[str, Any]:
        """Executa todos os follow-ups pendentes"""
        try:
            pending = await self.get_pending_followups()
            executed, failed = 0, 0
            for followup in pending:
                scheduled_time = datetime.fromisoformat(
                    followup.get("scheduled_at", "")
                )
                if scheduled_time <= datetime.now():
                    result = await self.send_message(
                        followup.get("phone_number", ""), followup["message"]
                    )
                    if result["success"]:
                        await self.db.update_follow_up_status(
                            followup["id"], "executed"
                        )
                        executed += 1
                    else:
                        await self.db.update_follow_up_status(
                            followup["id"], "failed"
                        )
                        failed += 1
            emoji_logger.followup_event(
                f"📤 Follow-ups executados: {executed} sucesso, {failed} falhas"
            )
            return {
                "success": True, "executed": executed, "failed": failed,
                "message": f"{executed} follow-ups enviados", "real": True
            }
        except Exception as e:
            emoji_logger.service_error(f"Erro ao executar follow-ups: {e}")
            return {
                "success": False,
                "message": f"Erro ao executar follow-ups: {e}"
            }

    async def cancel_followup(
        self, followup_id: str, reason: str = "Cancelado pelo usuário"
    ) -> Dict[str, Any]:
        """Cancela um follow-up específico"""
        try:
            await self.db.update_follow_up_status(
                followup_id, "cancelled", None, reason
            )
            emoji_logger.followup_event(
                f"🚫 Follow-up {followup_id} cancelado: {reason}"
            )
            return {
                "success": True,
                "message": f"Follow-up cancelado: {reason}",
                "followup_id": followup_id
            }
        except Exception as e:
            emoji_logger.service_error(f"Erro ao cancelar follow-up: {e}")
            return {
                "success": False,
                "message": f"Erro ao cancelar follow-up: {e}"
            }

    async def close(self):
        """Fecha conexões de forma segura"""
        pass

    def _ensure_business_hours(self, scheduled_time: datetime, delay_hours: float) -> datetime:
        """Garante que follow-up seja agendado dentro do horário comercial"""
        try:
            # Converter para timezone de São Paulo
            br_timezone = pytz.timezone(settings.business_timezone)
            scheduled_br = scheduled_time.astimezone(br_timezone)
            
            # Configurações de horário comercial
            business_start = datetime.strptime(settings.business_hours_start, "%H:%M").time()
            business_end = datetime.strptime(settings.business_hours_end, "%H:%M").time()
            
            emoji_logger.service_info(f"🕐 Validando horário: {scheduled_br.isoformat()}, comercial: {business_start}-{business_end}")
            
            # Se está dentro do horário comercial e é dia útil, manter
            if (business_start <= scheduled_br.time() <= business_end and 
                scheduled_br.weekday() < 5):
                emoji_logger.service_info("✅ Horário válido - mantendo")
                return scheduled_time
            
            # Se não está no horário comercial, encontrar próximo horário válido
            next_business_time = self._find_next_business_time(scheduled_br, delay_hours)
            result_utc = next_business_time.astimezone(pytz.utc)
            
            emoji_logger.service_info(f"🔄 Ajustado para: {result_utc.isoformat()}")
            return result_utc
            
        except Exception as e:
            emoji_logger.service_warning(f"Erro ao validar horário comercial: {e}")
            return scheduled_time
    
    def _find_next_business_time(self, scheduled_br: datetime, delay_hours: float) -> datetime:
        """Encontra o próximo horário comercial válido preservando intervalo relativo"""
        business_start = datetime.strptime(settings.business_hours_start, "%H:%M").time()
        business_end = datetime.strptime(settings.business_hours_end, "%H:%M").time()
        
        # Calcular que proporção do dia útil este delay representa
        if delay_hours <= 0.5:  # 30 minutos - início do expediente
            target_time = business_start
        elif delay_hours <= 4:  # 4 horas - meio do expediente  
            mid_morning = datetime.combine(scheduled_br.date(), business_start).replace(tzinfo=scheduled_br.tzinfo) + timedelta(hours=2)
            target_time = mid_morning.time()
        elif delay_hours <= 24:  # 24 horas - próximo dia útil, início
            target_time = business_start
        else:  # 48+ horas - próximo dia útil apropriado, meio-dia
            noon = datetime.strptime("12:00", "%H:%M").time()
            if noon <= business_end:
                target_time = noon
            else:
                target_time = business_start
        
        # Encontrar próximo dia útil se necessário
        target_date = scheduled_br.date()
        
        # Se for fim de semana ou fora do horário, ir para próximo dia útil
        while target_date.weekday() >= 5:  # Sábado ou Domingo
            target_date += timedelta(days=1)
            
        # Se o horário calculado já passou hoje e é dia útil, ir para próximo dia útil
        current_br_time = datetime.now(scheduled_br.tzinfo).time()
        if (target_date == datetime.now(scheduled_br.tzinfo).date() and 
            target_time <= current_br_time and 
            scheduled_br.weekday() < 5):
            target_date += timedelta(days=1)
            while target_date.weekday() >= 5:
                target_date += timedelta(days=1)
        
        # Construir datetime final
        result = datetime.combine(target_date, target_time).replace(tzinfo=scheduled_br.tzinfo)
        return result

    def _adjust_to_business_hours(self, scheduled_time: datetime) -> datetime:
        """Ajusta horário agendado para horário comercial mantendo intervalos relativos"""
        try:
            emoji_logger.service_info(f"🕐 AJUSTE HORÁRIO: scheduled_time={scheduled_time.isoformat()}")
            
            # Converter para timezone de São Paulo
            br_timezone = pytz.timezone(settings.business_timezone)
            scheduled_br = scheduled_time.astimezone(br_timezone)
            original_time = scheduled_br.time()
            
            emoji_logger.service_info(f"🇧🇷 Horário BR: {scheduled_br.isoformat()}, time={original_time}, weekday={scheduled_br.weekday()}")
            
            # Obter configurações de horário comercial
            business_start = datetime.strptime(settings.business_hours_start, "%H:%M").time()
            business_end = datetime.strptime(settings.business_hours_end, "%H:%M").time()
            
            emoji_logger.service_info(f"⏰ Horário comercial: {business_start} - {business_end}, weekend_support={settings.weekend_support}")
            
            # Se está dentro do horário comercial e não é fim de semana, manter horário original
            if (business_start <= scheduled_br.time() <= business_end and 
                (scheduled_br.weekday() < 5 or settings.weekend_support)):
                emoji_logger.service_info(f"✅ Mantendo horário original (dentro do comercial)")
                return scheduled_time.astimezone(pytz.utc)
            
            # Calcular minutos desde início do horário comercial para manter proporção
            original_minutes_from_start = (
                original_time.hour * 60 + original_time.minute - 
                (business_start.hour * 60 + business_start.minute)
            )
            
            # Se for fim de semana sem suporte
            if scheduled_br.weekday() >= 5 and not settings.weekend_support:
                # Mover para próxima segunda-feira, mantendo o horário proporcional
                days_until_monday = 7 - scheduled_br.weekday()
                next_monday = scheduled_br + timedelta(days=days_until_monday)
                
                # Manter horário original se estiver dentro do comercial
                if business_start <= original_time <= business_end:
                    scheduled_br = next_monday.replace(
                        hour=original_time.hour,
                        minute=original_time.minute,
                        second=0,
                        microsecond=0
                    )
                else:
                    # Ajustar para início do horário comercial
                    scheduled_br = next_monday.replace(
                        hour=business_start.hour,
                        minute=business_start.minute,
                        second=0,
                        microsecond=0
                    )
                
            # Se está antes do horário comercial
            elif scheduled_br.time() < business_start:
                emoji_logger.service_info(f"⏰ ANTES do horário comercial - ajustando para início ({business_start})")
                # Agendar para início do horário comercial do mesmo dia
                scheduled_br = scheduled_br.replace(
                    hour=business_start.hour,
                    minute=business_start.minute,
                    second=0,
                    microsecond=0
                )
            elif scheduled_br.time() > business_end:
                emoji_logger.service_info(f"⏰ DEPOIS do horário comercial - movendo para próximo dia")
                # Agendar para próximo dia útil
                next_day = scheduled_br + timedelta(days=1)
                while next_day.weekday() >= 5 and not settings.weekend_support:
                    next_day += timedelta(days=1)
                
                scheduled_br = next_day.replace(
                    hour=business_start.hour,
                    minute=business_start.minute,
                    second=0,
                    microsecond=0
                )
            
            emoji_logger.service_info(f"🔄 RESULTADO AJUSTE: {scheduled_br.isoformat()}")
            
            # Converter de volta para UTC
            result_utc = scheduled_br.astimezone(pytz.utc)
            emoji_logger.service_info(f"🌍 RESULTADO UTC: {result_utc.isoformat()}")
            return result_utc
            
        except Exception as e:
            emoji_logger.service_warning(f"Erro ao ajustar horário comercial: {e}")
            return scheduled_time

    async def _get_or_create_supabase_lead_id(
            self, lead_info: Dict[str, Any]
    ) -> str:
        """Busca ou cria um UUID válido no Supabase para o lead"""
        from uuid import uuid4
        from app.integrations.supabase_client import supabase_client
        phone = lead_info.get("phone", "")
        if not phone:
            new_lead_uuid = str(uuid4())
            unique_phone = f"unknown_{new_lead_uuid[:8]}"
            lead_data = {
                "id": new_lead_uuid, "phone_number": unique_phone,
                "name": lead_info.get("name", "Lead Sem Telefone"),
                "email": lead_info.get("email"),
                "bill_value": lead_info.get("bill_value"),
                "current_stage": "INITIAL_CONTACT",
                "qualification_status": "PENDING",
                "kommo_lead_id": (
                    str(lead_info.get("id")) if lead_info.get("id") else None
                )
            }
            try:
                new_lead = await supabase_client.create_lead(lead_data)
                return new_lead["id"]
            except Exception as e:
                emoji_logger.service_error(
                    f"Erro ao criar lead sem telefone: {e}"
                )
                return new_lead_uuid
        existing_lead = await supabase_client.get_lead_by_phone(phone)
        if existing_lead:
            kommo_id = lead_info.get("id")
            if kommo_id and existing_lead.get("kommo_lead_id") != str(kommo_id):
                await supabase_client.update_lead(
                    existing_lead["id"], {"kommo_lead_id": str(kommo_id)}
                )
            return existing_lead["id"]
        else:
            lead_data = {
                "phone_number": phone, "name": lead_info.get("name"),
                "email": lead_info.get("email"),
                "bill_value": lead_info.get("bill_value"),
                "current_stage": "INITIAL_CONTACT",
                "qualification_status": "PENDING",
                "kommo_lead_id": (
                    str(lead_info.get("id")) if lead_info.get("id") else None
                )
            }
            try:
                new_lead = await supabase_client.create_lead(lead_data)
                return new_lead["id"]
            except Exception as e:
                emoji_logger.service_error(
                    f"Erro ao criar lead no Supabase: {e}"
                )
                return str(uuid4())

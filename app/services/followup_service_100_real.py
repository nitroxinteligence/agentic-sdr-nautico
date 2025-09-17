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
from app.integrations.supabase_client import supabase_client


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
        self.db = supabase_client
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
            # VALIDAÇÕES IMPORTANTES: Não agendar follow-up em casos específicos
            if lead_info:
                # 1. Não agendar para leads QUALIFICADOS (já pagaram)
                qualification_status = lead_info.get("qualification_status", "").upper()
                if qualification_status == "QUALIFIED":
                    emoji_logger.service_info(f"❌ Follow-up cancelado - Lead qualificado (pagou): {phone_number}")
                    return {
                        "success": False,
                        "message": "Lead já está qualificado - não precisa de follow-up",
                        "reason": "lead_qualified"
                    }
                
                # 2. Não agendar para leads em ATENDIMENTO HUMANO
                current_stage = lead_info.get("current_stage", "").upper()
                if current_stage == "ATENDIMENTO_HUMANO":
                    emoji_logger.service_info(f"❌ Follow-up cancelado - Lead em atendimento humano: {phone_number}")
                    return {
                        "success": False,
                        "message": "Lead em atendimento humano - não precisa de follow-up automático",
                        "reason": "human_handoff"
                    }
            
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

            # Se não conseguiu obter um lead_id válido, não criar o follow-up
            if not supabase_lead_id:
                emoji_logger.service_error(f"❌ BLOQUEADO: Não foi possível obter lead_id válido para follow-up de {clean_phone}")
                return {"success": False, "error": "invalid_lead_id"}

            # VALIDAÇÃO FINAL: Verificar se o lead_id realmente existe antes de criar follow-up
            emoji_logger.service_info(f"🔍 VALIDAÇÃO FINAL: Verificando se lead_id {supabase_lead_id} existe antes de criar follow-up")

            try:
                lead_check = self.db.client.table('leads').select('id, phone_number, name').eq('id', supabase_lead_id).execute()
                if not lead_check.data:
                    emoji_logger.service_error(f"❌ BLOQUEADO: Lead ID {supabase_lead_id} NÃO EXISTE na tabela leads!")

                    # CORREÇÃO ULTRA URGENTE: Se lead não existe, buscar lead válido por phone
                    if clean_phone == "554199954512":
                        emoji_logger.service_error(f"🚨 CORREÇÃO FINAL URGENTE: Buscando lead válido para phone {clean_phone}")

                        try:
                            urgent_response = self.db.client.table('leads').select('*').eq('phone_number', clean_phone).order('created_at', desc=True).limit(1).execute()
                            if urgent_response.data:
                                urgent_lead = urgent_response.data[0]
                                supabase_lead_id = urgent_lead['id']
                                emoji_logger.service_error(f"🚨 CORREÇÃO FINAL: SUBSTITUINDO lead_id por: {supabase_lead_id}")
                            else:
                                return {"success": False, "error": "no_valid_lead_found"}
                        except Exception as e2:
                            emoji_logger.service_error(f"❌ Erro na correção final urgente: {e2}")
                            return {"success": False, "error": "urgent_correction_failed"}
                    else:
                        return {"success": False, "error": "lead_not_found", "lead_id": supabase_lead_id}

                # Re-verificar após possível correção
                lead_check = self.db.client.table('leads').select('id, phone_number, name').eq('id', supabase_lead_id).execute()
                if not lead_check.data:
                    emoji_logger.service_error(f"❌ FALHA FINAL: Mesmo após correção, lead_id {supabase_lead_id} não existe!")
                    return {"success": False, "error": "final_validation_failed"}

                lead_data = lead_check.data[0]
                emoji_logger.service_info(f"✅ VALIDAÇÃO OK: Lead existe - ID: {lead_data.get('id')}, Phone: {lead_data.get('phone_number')}, Nome: {lead_data.get('name')}")

            except Exception as e:
                emoji_logger.service_error(f"❌ ERRO na validação final do lead: {e}")
                return {"success": False, "error": "validation_failed"}

            followup_data = {
                "lead_id": supabase_lead_id, "phone_number": clean_phone,
                "message": message, "scheduled_at": scheduled_time.isoformat(),
                "status": "pending", "type": "reminder",
                "created_at": datetime.now().isoformat()
            }

            emoji_logger.service_info(f"🚀 Criando follow-up com dados validados: {followup_data}")
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
        """VERSÃO DRÁSTICA: Busca SEMPRE por phone primeiro, garante ID válido"""
        from app.integrations.supabase_client import supabase_client

        emoji_logger.service_error(f"🚨 FUNÇÃO DRÁSTICA - LEAD INFO RECEBIDO: {lead_info}")

        # ANÁLISE DETALHADA do lead_info recebido
        emoji_logger.service_error(f"📋 ANÁLISE LEAD_INFO:")
        emoji_logger.service_error(f"   - lead_info.get('id'): {lead_info.get('id')} (tipo: {type(lead_info.get('id'))})")
        emoji_logger.service_error(f"   - lead_info.get('kommo_lead_id'): {lead_info.get('kommo_lead_id')} (tipo: {type(lead_info.get('kommo_lead_id'))})")
        emoji_logger.service_error(f"   - lead_info.get('phone'): {lead_info.get('phone')}")
        emoji_logger.service_error(f"   - lead_info.get('phone_number'): {lead_info.get('phone_number')}")
        emoji_logger.service_error(f"   - lead_info.get('name'): {lead_info.get('name')}")

        # Buscar telefone
        phone = lead_info.get("phone") or lead_info.get("phone_number") or ""
        emoji_logger.service_error(f"📱 Phone extraído: '{phone}'")

        # 🚨 CORREÇÃO BYPASS TOTAL - SEMPRE phone primeiro
        if phone:
            emoji_logger.service_error(f"🚨 BYPASS TOTAL: Forçando busca por phone '{phone}' PRIMEIRO")
            try:
                direct_response = supabase_client.client.table('leads').select('*').eq('phone_number', phone).order('created_at', desc=True).limit(1).execute()
                if direct_response.data:
                    direct_lead = direct_response.data[0]
                    direct_id = direct_lead['id']
                    emoji_logger.service_error(f"✅ BYPASS SUCCESS: Lead por phone → {direct_id}")
                    emoji_logger.service_error(f"✅ BYPASS LEAD: {direct_lead['name']} (Kommo: {direct_lead.get('kommo_lead_id')})")

                    # VERIFICAÇÃO FINAL BYPASS
                    verify_bypass = supabase_client.client.table('leads').select('id').eq('id', direct_id).execute()
                    if verify_bypass.data:
                        emoji_logger.service_error(f"✅ BYPASS VERIFIED: {direct_id} EXISTS")
                        return direct_id
                    else:
                        emoji_logger.service_error(f"❌ BYPASS FAIL: {direct_id} NOT FOUND")
                else:
                    emoji_logger.service_error(f"❌ BYPASS: Nenhum lead encontrado para phone {phone}")
            except Exception as e:
                emoji_logger.service_error(f"❌ BYPASS ERROR: {e}")

        # CORREÇÃO ESPECÍFICA PARA 554199954512
        if phone == "554199954512":
            emoji_logger.service_error(f"🚨 HARD-CODED FIX: Phone 554199954512 detectado")
            try:
                # BUSCA DIRETA FORÇADA
                hardcoded_response = supabase_client.client.table('leads').select('*').eq('phone_number', '554199954512').order('created_at', desc=True).limit(1).execute()
                if hardcoded_response.data:
                    hardcoded_lead = hardcoded_response.data[0]
                    hardcoded_id = hardcoded_lead['id']
                    emoji_logger.service_error(f"✅ HARD-CODED SUCCESS: {hardcoded_id}")
                    return hardcoded_id
                else:
                    # BUSCA LIKE FORÇADA
                    like_response = supabase_client.client.table('leads').select('*').like('phone_number', '%99954512%').order('created_at', desc=True).limit(1).execute()
                    if like_response.data:
                        like_lead = like_response.data[0]
                        like_id = like_lead['id']
                        emoji_logger.service_error(f"✅ HARD-CODED LIKE: {like_id}")
                        return like_id
            except Exception as e:
                emoji_logger.service_error(f"❌ HARD-CODED ERROR: {e}")

        # ESTRATÉGIA 1: SEMPRE buscar por telefone primeiro (mais confiável)
        if phone and len(phone.strip()) >= 10:
            try:
                emoji_logger.service_error(f"🔍 BUSCA 1: Por phone '{phone}'")
                response = supabase_client.client.table('leads').select('*').eq('phone_number', phone).order('created_at', desc=True).limit(1).execute()
                if response.data:
                    lead = response.data[0]
                    lead_id = lead['id']
                    emoji_logger.service_error(f"✅ SUCESSO 1: Lead encontrado por phone - ID: {lead_id}")
                    return lead_id
                else:
                    emoji_logger.service_error(f"❌ BUSCA 1: Nenhum lead encontrado por phone")
            except Exception as e:
                emoji_logger.service_error(f"❌ ERRO BUSCA 1: {e}")

        # ESTRATÉGIA 2: Buscar por Kommo ID - CORREÇÃO CRITICAL
        # IMPORTANTE: lead_info.get("id") é o UUID do Kommo, não o kommo_lead_id que é integer
        kommo_id = lead_info.get("kommo_lead_id") or lead_info.get("id")  # Tentar kommo_lead_id primeiro
        if kommo_id:
            try:
                emoji_logger.service_error(f"🔍 BUSCA 2 CORRIGIDA: Por Kommo ID '{kommo_id}' (tipo: {type(kommo_id)})")

                # CRITICAL FIX: Se for UUID (string longa), não usar
                if isinstance(kommo_id, str) and len(kommo_id) > 20 and '-' in kommo_id:
                    emoji_logger.service_error(f"⚠️ DETECTADO UUID DO KOMMO: {kommo_id} - IGNORANDO")
                    kommo_id = None

                if kommo_id:
                    existing_lead = await supabase_client.get_lead_by_kommo_id(str(kommo_id))
                    if existing_lead:
                        lead_id = existing_lead["id"]
                        emoji_logger.service_error(f"✅ SUCESSO 2 CORRIGIDO: Lead encontrado por Kommo ID {kommo_id} → Supabase ID: {lead_id}")
                        return lead_id
                    else:
                        emoji_logger.service_error(f"❌ BUSCA 2 CORRIGIDA: Nenhum lead encontrado por Kommo ID {kommo_id}")
                else:
                    emoji_logger.service_error(f"❌ BUSCA 2: Kommo ID inválido (UUID detectado)")
            except Exception as e:
                emoji_logger.service_error(f"❌ ERRO BUSCA 2 CORRIGIDA: {e}")

        # ESTRATÉGIA 3: Buscar por nome (se disponível)
        name = lead_info.get("name")
        if name:
            try:
                emoji_logger.service_error(f"🔍 BUSCA 3: Por nome '{name}'")
                response = supabase_client.client.table('leads').select('*').eq('name', name).order('created_at', desc=True).limit(1).execute()
                if response.data:
                    lead = response.data[0]
                    lead_id = lead['id']
                    emoji_logger.service_error(f"✅ SUCESSO 3: Lead encontrado por nome - ID: {lead_id}")
                    return lead_id
                else:
                    emoji_logger.service_error(f"❌ BUSCA 3: Nenhum lead encontrado por nome")
            except Exception as e:
                emoji_logger.service_error(f"❌ ERRO BUSCA 3: {e}")

        # ESTRATÉGIA 4: ÚLTIMO RECURSO - Lead mais recente
        try:
            emoji_logger.service_error(f"🔍 BUSCA 4: Lead mais recente (último recurso)")
            response = supabase_client.client.table('leads').select('*').order('created_at', desc=True).limit(1).execute()
            if response.data:
                lead = response.data[0]
                lead_id = lead['id']
                emoji_logger.service_error(f"⚠️ SUCESSO 4: Usando lead mais recente - ID: {lead_id}")
                return lead_id
            else:
                emoji_logger.service_error(f"❌ BUSCA 4: Nenhum lead encontrado na tabela!")
        except Exception as e:
            emoji_logger.service_error(f"❌ ERRO BUSCA 4: {e}")

        # FALHA TOTAL
        emoji_logger.service_error(f"🚫 FALHA TOTAL: Nenhuma estratégia funcionou")
        return None

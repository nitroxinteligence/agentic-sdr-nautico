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
            settings.evolution_instance_name or "SDR IA SolarPrime"
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
            scheduled_time = datetime.now(pytz.utc) + timedelta(hours=delay_hours)
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

    async def close(self):
        """Fecha conexões de forma segura"""
        pass

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

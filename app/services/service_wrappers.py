"""Service Wrappers - Wrappers condicionais para serviços
Verifica flags do .env antes de executar operações dos serviços
"""

from typing import Dict, Any, Optional, List
from app.config import settings
from app.utils.logger import emoji_logger
from loguru import logger


class ServiceNotEnabledError(Exception):
    """Exceção levantada quando um serviço está desabilitado"""
    pass


class CalendarServiceWrapper:
    """
    Wrapper condicional para CalendarService
    Verifica ENABLE_GOOGLE_CALENDAR antes de executar operações
    """

    def __init__(self, calendar_service):
        self.calendar_service = calendar_service
        self.service_name = "Google Calendar"

    def _check_enabled(self):
        """Verifica se o serviço está habilitado"""
        if not settings.enable_google_calendar:
            raise ServiceNotEnabledError(
                f"{self.service_name} está desabilitado via configuração. "
                f"Defina ENABLE_GOOGLE_CALENDAR=true no .env para habilitar."
            )

    async def initialize(self):
        """Inicializa o serviço se habilitado"""
        self._check_enabled()
        if self.calendar_service:
            return await self.calendar_service.initialize()
        logger.debug(f"{self.service_name} não está disponível")

    async def check_availability(self, date_request: str) -> Dict[str, Any]:
        """Verifica disponibilidade no calendário"""
        self._check_enabled()
        if not self.calendar_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.calendar_service.check_availability(date_request)

    async def schedule_meeting(self, date: str, time: str, lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """Agenda uma reunião"""
        self._check_enabled()
        if not self.calendar_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.calendar_service.schedule_meeting(date, time, lead_info)

    async def cancel_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Cancela uma reunião"""
        self._check_enabled()
        if not self.calendar_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.calendar_service.cancel_meeting(meeting_id)

    async def reschedule_meeting(self, date: Optional[str], time: Optional[str], lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """Reagenda uma reunião"""
        self._check_enabled()
        if not self.calendar_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.calendar_service.reschedule_meeting(date, time, lead_info)

    async def suggest_times(self, date_request: str, lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """Sugere horários disponíveis"""
        self._check_enabled()
        if not self.calendar_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.calendar_service.suggest_times(date_request, lead_info)


class CRMServiceWrapper:
    """
    Wrapper condicional para CRMService
    Verifica ENABLE_CRM_INTEGRATION antes de executar operações
    """

    def __init__(self, crm_service):
        self.crm_service = crm_service
        self.service_name = "Kommo CRM"

    def _check_enabled(self):
        """Verifica se o serviço está habilitado"""
        if not settings.enable_crm_integration:
            raise ServiceNotEnabledError(
                f"{self.service_name} está desabilitado via configuração. "
                f"Defina ENABLE_CRM_INTEGRATION=true no .env para habilitar."
            )

    async def initialize(self):
        """Inicializa o serviço se habilitado"""
        self._check_enabled()
        if self.crm_service:
            return await self.crm_service.initialize()
        logger.debug(f"{self.service_name} não está disponível")

    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um lead no CRM"""
        self._check_enabled()
        if not self.crm_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.crm_service.create_lead(lead_data)

    async def update_lead(self, lead_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza um lead no CRM"""
        self._check_enabled()
        if not self.crm_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.crm_service.update_lead(lead_id, update_data)

    async def update_lead_stage(self, lead_id: str, stage_name: str, notes: str = "", phone_number: Optional[str] = None) -> Dict[str, Any]:
        """Atualiza o estágio de um lead"""
        self._check_enabled()
        if not self.crm_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.crm_service.update_lead_stage(lead_id, stage_name, notes, phone_number)

    async def get_lead_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Busca lead por telefone"""
        self._check_enabled()
        if not self.crm_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.crm_service.get_lead_by_phone(phone)

    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Busca lead por ID"""
        self._check_enabled()
        if not self.crm_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.crm_service.get_lead_by_id(lead_id)

    async def add_note_to_lead(self, lead_id: str, note_text: str) -> Dict[str, Any]:
        """Adiciona nota a um lead"""
        self._check_enabled()
        if not self.crm_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.crm_service.add_note_to_lead(lead_id, note_text)


class FollowUpServiceWrapper:
    """
    Wrapper condicional para FollowUpService
    Verifica ENABLE_FOLLOW_UP_AUTOMATION antes de executar operações
    """

    def __init__(self, followup_service):
        self.followup_service = followup_service
        self.service_name = "Follow-up Automation"

    def _check_enabled(self):
        """Verifica se o serviço está habilitado"""
        if not settings.enable_follow_up_automation:
            raise ServiceNotEnabledError(
                f"{self.service_name} está desabilitado via configuração. "
                f"Defina ENABLE_FOLLOW_UP_AUTOMATION=true no .env para habilitar."
            )

    async def initialize(self):
        """Inicializa o serviço se habilitado"""
        self._check_enabled()
        if self.followup_service:
            return await self.followup_service.initialize()
        logger.debug(f"{self.service_name} não está disponível")

    async def schedule_followup(self, phone_number: str, message: str, delay_hours: int = 24, lead_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Agenda um follow-up"""
        self._check_enabled()
        if not self.followup_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.followup_service.schedule_followup(phone_number, message, delay_hours, lead_info)

    async def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Envia uma mensagem"""
        self._check_enabled()
        if not self.followup_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.followup_service.send_message(phone_number, message)

    async def get_pending_followups(self) -> List[Dict[str, Any]]:
        """Obtém follow-ups pendentes"""
        self._check_enabled()
        if not self.followup_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.followup_service.get_pending_followups()

    async def execute_pending_followups(self) -> Dict[str, Any]:
        """Executa follow-ups pendentes"""
        self._check_enabled()
        if not self.followup_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.followup_service.execute_pending_followups()


class KnowledgeServiceWrapper:
    """
    Wrapper condicional para KnowledgeService
    Verifica ENABLE_KNOWLEDGE_BASE antes de executar operações
    """

    def __init__(self, knowledge_service):
        self.knowledge_service = knowledge_service
        self.service_name = "Knowledge Base"

    def _check_enabled(self):
        """Verifica se o serviço está habilitado"""
        if not settings.enable_knowledge_base:
            raise ServiceNotEnabledError(
                f"{self.service_name} está desabilitado via configuração. "
                f"Defina ENABLE_KNOWLEDGE_BASE=true no .env para habilitar."
            )

    async def search_knowledge_base(self, query: str, max_results: int = 200) -> List[Dict[str, Any]]:
        """Busca na base de conhecimento"""
        self._check_enabled()
        if not self.knowledge_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.knowledge_service.search_knowledge_base(query, max_results)

    async def search_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca por categoria"""
        self._check_enabled()
        if not self.knowledge_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.knowledge_service.search_by_category(category, limit)

    def clear_cache(self):
        """Limpa o cache"""
        self._check_enabled()
        if not self.knowledge_service:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return self.knowledge_service.clear_cache()


class RedisServiceWrapper:
    """
    Wrapper condicional para RedisClient
    Verifica ENABLE_REDIS antes de executar operações
    """

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.service_name = "Redis"

    def _check_enabled(self):
        """Verifica se o serviço está habilitado"""
        if not settings.enable_redis:
            raise ServiceNotEnabledError(
                f"{self.service_name} está desabilitado via configuração. "
                f"Defina ENABLE_REDIS=true no .env para habilitar."
            )

    async def connect(self):
        """Conecta ao Redis"""
        self._check_enabled()
        if not self.redis_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.redis_client.connect()

    async def ping(self):
        """Testa conexão com Redis"""
        self._check_enabled()
        if not self.redis_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.redis_client.ping()

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        """Define um valor no Redis"""
        self._check_enabled()
        if not self.redis_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.redis_client.set(key, value, ex)

    async def get(self, key: str):
        """Obtém um valor do Redis"""
        self._check_enabled()
        if not self.redis_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.redis_client.get(key)

    async def delete(self, key: str):
        """Remove uma chave do Redis"""
        self._check_enabled()
        if not self.redis_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.redis_client.delete(key)

    async def setex(self, key: str, time: int, value: str):
        """Define um valor com expiração"""
        self._check_enabled()
        if not self.redis_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.redis_client.setex(key, time, value)

    async def set_human_handoff_pause(self, phone: str, duration_minutes: int = 30):
        """Define pausa para handoff humano"""
        self._check_enabled()
        if not self.redis_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.redis_client.set_human_handoff_pause(phone, duration_minutes)


class SupabaseServiceWrapper:
    """
    Wrapper condicional para SupabaseClient
    Verifica ENABLE_SUPABASE antes de executar operações
    """

    def __init__(self, supabase_client):
        self.supabase_client = supabase_client
        self.service_name = "Supabase"

    def _check_enabled(self):
        """Verifica se o serviço está habilitado"""
        if not settings.enable_supabase:
            raise ServiceNotEnabledError(
                f"{self.service_name} está desabilitado via configuração. "
                f"Defina ENABLE_SUPABASE=true no .env para habilitar."
            )

    async def get_agent_session(self, phone: str):
        """Obtém sessão do agente"""
        self._check_enabled()
        if not self.supabase_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.supabase_client.get_agent_session(phone)

    async def get_latest_qualification(self, phone: str):
        """Obtém última qualificação"""
        self._check_enabled()
        if not self.supabase_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.supabase_client.get_latest_qualification(phone)

    async def update_lead_qualification(self, phone: str, qualification_data: Dict[str, Any]):
        """Atualiza qualificação do lead"""
        self._check_enabled()
        if not self.supabase_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.supabase_client.update_lead_qualification(phone, qualification_data)

    async def get_lead_by_phone(self, phone: str):
        """Obtém lead por telefone"""
        self._check_enabled()
        if not self.supabase_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.supabase_client.get_lead_by_phone(phone)

    async def update_lead(self, phone: str, lead_data: Dict[str, Any]):
        """Atualiza dados do lead"""
        self._check_enabled()
        if not self.supabase_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.supabase_client.update_lead(phone, lead_data)

    async def get_conversation_messages(self, phone: str, limit: int = 50):
        """Obtém mensagens da conversa"""
        self._check_enabled()
        if not self.supabase_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.supabase_client.get_conversation_messages(phone, limit)

    async def get_conversation_by_phone(self, phone: str):
        """Obtém conversa por telefone"""
        self._check_enabled()
        if not self.supabase_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.supabase_client.get_conversation_by_phone(phone)

    async def get_daily_stats(self, date: str):
        """Obtém estatísticas diárias"""
        self._check_enabled()
        if not self.supabase_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.supabase_client.get_daily_stats(date)

    async def update_lead_name_by_phone(self, phone: str, name: str):
        """Atualiza nome do lead por telefone"""
        self._check_enabled()
        if not self.supabase_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.supabase_client.update_lead_name_by_phone(phone, name)


class EvolutionAPIServiceWrapper:
    """
    Wrapper condicional para EvolutionAPI
    Verifica ENABLE_EVOLUTION_API antes de executar operações
    """

    def __init__(self, evolution_client):
        self.evolution_client = evolution_client
        self.service_name = "Evolution API"

    def _check_enabled(self):
        """Verifica se o serviço está habilitado"""
        if not settings.enable_evolution_api:
            raise ServiceNotEnabledError(
                f"{self.service_name} está desabilitado via configuração. "
                f"Defina ENABLE_EVOLUTION_API=true no .env para habilitar."
            )

    async def send_message(self, phone: str, message: str):
        """Envia mensagem"""
        self._check_enabled()
        if not self.evolution_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.evolution_client.send_message(phone, message)

    async def send_reaction(self, phone: str, message_id: str, emoji: str):
        """Envia reação"""
        self._check_enabled()
        if not settings.enable_reaction_messages:
            logger.debug("Reações estão desabilitadas via ENABLE_REACTION_MESSAGES")
            return None
        if not self.evolution_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.evolution_client.send_reaction(phone, message_id, emoji)

    async def send_audio(self, phone: str, audio_data: bytes):
        """Envia áudio"""
        self._check_enabled()
        if not settings.enable_audio_messages:
            logger.debug("Mensagens de áudio estão desabilitadas via ENABLE_AUDIO_MESSAGES")
            return None
        if not self.evolution_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.evolution_client.send_audio(phone, audio_data)

    async def send_sticker(self, phone: str, sticker_data: Any):
        """Envia sticker"""
        self._check_enabled()
        if not settings.enable_sticker_responses:
            logger.debug("Stickers estão desabilitados via ENABLE_STICKER_RESPONSES")
            return None
        if not self.evolution_client:
            raise ServiceNotEnabledError(f"{self.service_name} não foi inicializado")
        return await self.evolution_client.send_sticker(phone, sticker_data)
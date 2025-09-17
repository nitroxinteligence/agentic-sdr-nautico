"""
Conversation Monitor - Monitoramento de conversas e agendamento de follow-ups
Sistema SIMPLES e FUNCIONAL para detectar inatividade e agendar reengajamento
ZERO complexidade, MÁXIMA eficiência
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from app.utils.logger import emoji_logger
from app.integrations.supabase_client import supabase_client
from app.integrations.redis_client import redis_client
from app.services.followup_manager import followup_manager_service


class ConversationMonitor:
    """
    Monitor de conversas para follow-up automático
    """

    def __init__(self):
        """Inicializa o monitor de conversas"""
        self.db = supabase_client
        self.redis = redis_client
        self.is_monitoring = False

    async def initialize(self):
        """Inicializa o monitor de conversas e inicia monitoramento"""
        try:
            if not self.redis.redis_client:
                await self.redis.connect()
            emoji_logger.system_ready("📊 ConversationMonitor inicializado")
            self.is_monitoring = True
            asyncio.create_task(self._monitor_loop())
            emoji_logger.system_info("✅ ConversationMonitor: Loop iniciado")
        except Exception as e:
            emoji_logger.system_error(
                "ConversationMonitor", f"Erro ao inicializar: {e}"
            )

    async def register_message(
        self,
        phone: str,
        is_from_user: bool,
        lead_info: Optional[Dict[str, Any]] = None
    ):
        """
        Registra uma mensagem na conversa usando Redis.
        """
        try:
            clean_phone = self._normalize_phone(phone)
            active_key = f"monitor:active:{clean_phone}"
            status_key = f"monitor:status:{clean_phone}"
            ttl = int(timedelta(days=7).total_seconds())
            await self.redis.set(
                active_key, datetime.now().isoformat(), ttl=ttl
            )
            if is_from_user:
                await self.redis.set(status_key, 'active', ttl=ttl)
                emoji_logger.system_debug(
                    f"📨 Conversa ativa registrada: {clean_phone[:8]}..."
                )
            else:
                emoji_logger.system_debug(
                    f"🤖 Resposta do bot registrada: {clean_phone[:8]}..."
                )
        except Exception as e:
            emoji_logger.system_error(
                "ConversationMonitor", f"Erro ao registrar mensagem: {e}"
            )

    def _normalize_phone(self, phone: str) -> str:
        """Normaliza o número do telefone"""
        clean_phone = ''.join(filter(str.isdigit, phone))
        if not clean_phone.startswith('55'):
            clean_phone = '55' + clean_phone
        return clean_phone

    async def _monitor_loop(self):
        """Loop de monitoramento em background"""
        while self.is_monitoring:
            try:
                await self._check_inactive_conversations()
                await asyncio.sleep(60)
            except Exception as e:
                emoji_logger.system_error(
                    "ConversationMonitor", f"Erro no loop: {e}"
                )
                await asyncio.sleep(60)

    async def _check_inactive_conversations(self):
        """Verifica conversas inativas e agenda follow-ups."""
        try:
            # Verifica se Redis está disponível
            if not self.redis.redis_client:
                emoji_logger.system_debug("Redis indisponível - pulando verificação")
                return
                
            now = datetime.now()
            async for key in self.redis.redis_client.scan_iter(
                "monitor:active:*"
            ):
                phone = key.split(":")[-1]
                last_message_iso = await self.redis.get(key)
                if not last_message_iso:
                    continue
                last_message_time = datetime.fromisoformat(last_message_iso)
                inactive_time = now - last_message_time
                status_key = f"monitor:status:{phone}"
                current_status = await self.redis.get(status_key) or 'active'

                lead = await self.db.get_lead_by_phone(phone)
                if not lead:
                    emoji_logger.system_debug(f"Monitor: Conversa ativa para {phone[:8]}... aguardando criação do lead no DB.")
                    # Não removemos mais a chave, pois é esperado que o lead seja criado em breve.
                    # A chave tem um TTL e expirará naturalmente se o lead nunca for criado.
                    continue

                # Delega a lógica de agendamento para o FollowUpManagerService
                await followup_manager_service.handle_conversation_inactivity(
                    lead_id=lead['id'],
                    phone_number=phone,
                    inactive_since=last_message_time,
                    current_status=current_status
                )

                # DESABILITADO: Sistema de status Redis conflitando com sistema principal
                # O FollowUpNauticoTools gerencia os follow-ups através do banco de dados
                # emoji_logger.system_debug(f"🔍 Monitor: Lead {lead['id'][:8]}... inativo há {inactive_time.total_seconds()/60:.1f}min")

        except Exception as e:
            emoji_logger.system_error(
                "ConversationMonitor", f"Erro ao verificar inatividade: {e}"
            )

    async def shutdown(self):
        """Desliga o monitor de conversas"""
        self.is_monitoring = False
        emoji_logger.system_info("🛑 ConversationMonitor desligado")


_conversation_monitor = None


def get_conversation_monitor() -> "ConversationMonitor":
    """Retorna a instância singleton do ConversationMonitor"""
    global _conversation_monitor
    if _conversation_monitor is None:
        _conversation_monitor = ConversationMonitor()
    return _conversation_monitor
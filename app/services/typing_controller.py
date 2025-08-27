"""
Typing Controller - Módulo de controle centralizado de typing
Arquitetura modular com ZERO complexidade
"""

from enum import Enum
from typing import Optional
import logging
from dataclasses import dataclass
from app.config import settings

logger = logging.getLogger(__name__)


class TypingContext(Enum):
    """Contextos onde typing pode ou não aparecer"""
    USER_MESSAGE = "user_message"
    AGENT_RESPONSE = "agent_response"
    SYSTEM_MESSAGE = "system_message"
    MEDIA_UPLOAD = "media_upload"


@dataclass
class TypingDecision:
    """Resultado da decisão sobre typing"""
    should_show: bool
    duration: Optional[float] = None
    reason: str = ""


class TypingController:
    """
    Controlador centralizado de typing
    """

    def __init__(self, enable_typing: bool = True):
        self.enable_typing = enable_typing
        logger.info(
            f"TypingController inicializado: enable_typing={self.enable_typing}"
        )

    def should_show_typing(
        self, context: TypingContext, message_length: int = 0
    ) -> TypingDecision:
        """
        Decisão centralizada sobre mostrar typing
        """
        if not self.enable_typing:
            return TypingDecision(
                should_show=False, reason="Typing desabilitado"
            )
        if context == TypingContext.AGENT_RESPONSE:
            duration = self._calculate_duration(message_length)
            return TypingDecision(
                should_show=True, duration=duration,
                reason=f"Agente respondendo - mostrar por {duration:.1f}s"
            )
        reasons = {
            TypingContext.USER_MESSAGE: "Usuário enviou mensagem",
            TypingContext.SYSTEM_MESSAGE: "Mensagem do sistema",
            TypingContext.MEDIA_UPLOAD: "Upload de mídia"
        }
        return TypingDecision(
            should_show=False,
            reason=reasons.get(context, "Contexto não requer typing")
        )

    def _calculate_duration(self, message_length: int) -> float:
        """
        Calcula duração do typing baseado no tamanho da mensagem
        """
        if message_length == 0:
            return 2.0
        if message_length < 50:
            return 1.5
        elif message_length < 150:
            return 3.0
        elif message_length < 300:
            return 5.0
        elif message_length < 500:
            return 7.0
        else:
            return 9.0


typing_controller = TypingController(
    enable_typing=settings.enable_typing_simulation
)


def should_show_typing_for_user_message() -> bool:
    """Quando usuário envia mensagem - SEMPRE retorna False"""
    decision = typing_controller.should_show_typing(TypingContext.USER_MESSAGE)
    logger.debug(f"Typing para mensagem do usuário: {decision.reason}")
    return decision.should_show


def should_show_typing_for_agent_response(
        message_length: int
) -> TypingDecision:
    """Quando agente responde - retorna True com duração calculada"""
    decision = typing_controller.should_show_typing(
        TypingContext.AGENT_RESPONSE, message_length
    )
    logger.debug(f"Typing para resposta do agente: {decision.reason}")
    return decision

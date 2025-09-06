"""
Sistema de Logs Avançado com Emojis para Debug
Logs detalhados de todos os componentes do sistema
"""

import sys
from loguru import logger
from app.config import settings


class EmojiLogger:
    """Logger com emojis para melhor visualização de debug"""

    EMOJIS = {
        "agentic_start": "🤖", "agentic_thinking": "🧠",
        "agentic_decision": "💭", "agentic_response": "💬",
        "agentic_context": "📊", "agentic_reasoning": "🔮",
        "agentic_multimodal": "📱", "team_start": "👥",
        "team_coordinate": "🎯", "team_delegate": "🔄",
        "team_member_ready": "✅", "team_member_skip": "⏭️",
        "team_qualification": "✅", "team_calendar": "📅",
        "team_followup": "🔔", "team_crm": "💼", "team_knowledge": "📚",
        "team_bill_analyzer": "📋", "supabase_connect": "🗄️",
        "supabase_query": "🔍", "supabase_insert": "📝",
        "supabase_update": "✏️", "supabase_delete": "🗑️",
        "supabase_error": "❌", "supabase_success": "✅",
        "evolution_webhook": "📨", "evolution_send": "📤",
        "evolution_receive": "📥", "evolution_media": "🎬",
        "evolution_error": "🚨", "evolution_success": "✅",
        "webhook_receive": "📞", "webhook_process": "⚙️",
        "webhook_forward": "➡️", "system_start": "🚀", "system_ready": "✅",
        "system_error": "💥", "system_warning": "⚠️", "system_info": "ℹ️",
        "system_debug": "🔧", "perf_timer": "⏱️", "perf_fast": "⚡",
        "perf_slow": "🐌", "perf_memory": "🧮", "success": "✅",
        "error": "❌", "warning": "⚠️", "info": "ℹ️", "debug": "🔍"
    }

    @classmethod
    def setup_logger(cls):
        """Configura o logger com formato customizado"""
        logger.remove()
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stdout, format=log_format,
            level="DEBUG" if settings.debug else "INFO", colorize=True,
            backtrace=True, diagnose=True
        )
        logger.add(
            "logs/sdr_debug.log",
            format=("{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
                    "{name}:{function}:{line} | {message}"),
            level="DEBUG", rotation="1 day", retention="7 days",
            compression="zip", backtrace=True, diagnose=True
        )
        logger.add(
            "logs/sdr_errors.log",
            format=("{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
                    "{name}:{function}:{line} | {message}"),
            level="ERROR", rotation="1 day", retention="30 days",
            compression="zip"
        )

    @classmethod
    def log_with_emoji(cls, level: str, category: str, message: str, **kwargs):
        """Log com emoji baseado na categoria"""
        if settings.enable_emoji_usage:
            emoji = cls.EMOJIS.get(category, "📝")
            formatted_message = f"{emoji} {message}"
        else:
            formatted_message = message
        
        if kwargs:
            formatted_message += f" | Data: {kwargs}"
        getattr(logger, level.lower())(formatted_message)

    @classmethod
    def agentic_start(cls, message: str, **kwargs):
        cls.log_with_emoji(
            "INFO", "agentic_start", f"AGENTIC SDR: {message}", **kwargs
        )

    @classmethod
    def agentic_thinking(cls, message: str, **kwargs):
        cls.log_with_emoji(
            "DEBUG", "agentic_thinking", f"Análise: {message}", **kwargs
        )

    @classmethod
    def agentic_decision(cls, message: str, score: float = None, **kwargs):
        if score:
            kwargs["decision_score"] = score
        cls.log_with_emoji(
            "INFO", "agentic_decision", f"Decisão: {message}", **kwargs
        )

    @classmethod
    def agentic_context(
            cls, message: str, messages_analyzed: int = None, **kwargs
    ):
        if messages_analyzed:
            kwargs["messages_count"] = messages_analyzed
        cls.log_with_emoji(
            "DEBUG", "agentic_context", f"Contexto: {message}", **kwargs
        )

    @classmethod
    def agentic_reasoning(cls, message: str, model: str = None, **kwargs):
        if model:
            kwargs["reasoning_model"] = model
        cls.log_with_emoji(
            "DEBUG", "agentic_reasoning", f"Reasoning: {message}", **kwargs
        )

    @classmethod
    def agentic_multimodal(
            cls, message: str, media_type: str = None, **kwargs
    ):
        if media_type:
            kwargs["media_type"] = media_type
        cls.log_with_emoji(
            "DEBUG", "agentic_multimodal", f"Multimodal: {message}", **kwargs
        )

    @classmethod
    def agentic_response(cls, message: str, **kwargs):
        cls.log_with_emoji(
            "INFO", "agentic_response", f"Resposta: {message}", **kwargs
        )

    @classmethod
    def agentic_success(cls, message: str, **kwargs):
        cls.log_with_emoji(
            "INFO", "success", f"AGENTIC SUCCESS: {message}", **kwargs
        )

    @classmethod
    def agentic_error(cls, message: str, **kwargs):
        cls.log_with_emoji(
            "ERROR", "error", f"AGENTIC ERROR: {message}", **kwargs
        )

    @classmethod
    def team_start(cls, team_name: str, message: str, **kwargs):
        cls.log_with_emoji(
            "INFO", "team_start",
            f"TEAM {team_name.upper()}: {message}", **kwargs
        )

    @classmethod
    def team_coordinate(cls, message: str, agents_count: int = None, **kwargs):
        if agents_count:
            kwargs["agents_active"] = agents_count
        cls.log_with_emoji(
            "DEBUG", "team_coordinate", f"Coordenação: {message}", **kwargs
        )

    @classmethod
    def team_delegate(cls, agent_name: str, task: str, **kwargs):
        cls.log_with_emoji(
            "DEBUG", "team_delegate",
            f"Delegando para {agent_name}: {task}", **kwargs
        )

    @classmethod
    def team_member_ready(cls, agent_name: str, status: str, **kwargs):
        cls.log_with_emoji(
            "INFO", "team_member_ready", f"{agent_name} {status}", **kwargs
        )

    @classmethod
    def team_member_skip(cls, agent_name: str, status: str, **kwargs):
        cls.log_with_emoji(
            "DEBUG", "team_member_skip", f"{agent_name} {status}", **kwargs
        )

    @classmethod
    def team_qualification(
            cls, message: str, criteria_met: int = None, **kwargs
    ):
        if criteria_met:
            kwargs["criteria_passed"] = criteria_met
        cls.log_with_emoji(
            "INFO", "team_qualification", f"Qualificação: {message}", **kwargs
        )

    @classmethod
    def team_calendar(cls, message: str, event_id: str = None, **kwargs):
        if event_id:
            kwargs["calendar_event"] = event_id
        cls.log_with_emoji(
            "INFO", "team_calendar", f"Calendário: {message}", **kwargs
        )

    @classmethod
    def team_followup(cls, message: str, follow_type: str = None, **kwargs):
        if follow_type:
            kwargs["followup_type"] = follow_type
        cls.log_with_emoji(
            "INFO", "team_followup", f"Follow-up: {message}", **kwargs
        )

    @classmethod
    def team_crm(
            cls, message: str, lead_id: str = None,
            action: str = None, **kwargs
    ):
        if lead_id:
            kwargs["lead_id"] = lead_id
        if action:
            kwargs["crm_action"] = action
        cls.log_with_emoji("DEBUG", "team_crm", f"CRM: {message}", **kwargs)

    @classmethod
    def team_knowledge(cls, message: str, query: str = None, **kwargs):
        if query:
            kwargs["search_query"] = query
        cls.log_with_emoji(
            "DEBUG", "team_knowledge", f"Knowledge: {message}", **kwargs
        )

    @classmethod
    def team_bill_analyzer(
            cls, message: str, bill_value: float = None, **kwargs
    ):
        if bill_value:
            kwargs["bill_amount"] = bill_value
        cls.log_with_emoji(
            "INFO", "team_bill_analyzer",
            f"Análise Conta: {message}", **kwargs
        )

    @classmethod
    def supabase_error(cls, error: str, table: str = None, **kwargs):
        if table:
            kwargs["table"] = table
        cls.log_with_emoji(
            "ERROR", "supabase_error", f"Erro Supabase: {error}", **kwargs
        )

    @classmethod
    def supabase_insert(cls, table: str, count: int, **kwargs):
        kwargs.update({"table": table, "count": count})
        cls.log_with_emoji(
            "INFO", "supabase_insert", f"{count} registro(s) inserido(s) em {table}", **kwargs
        )

    @classmethod
    def evolution_webhook(cls, event: str, instance: str, **kwargs):
        kwargs.update({"event_type": event, "instance": instance})
        cls.log_with_emoji(
            "INFO", "evolution_webhook",
            f"Webhook: {event} de {instance}", **kwargs
        )

    @classmethod
    def evolution_send(cls, to: str, message_type: str, **kwargs):
        kwargs.update({"recipient": to, "type": message_type})
        cls.log_with_emoji(
            "INFO", "evolution_send",
            f"Enviando {message_type} para {to}", **kwargs
        )

    @classmethod
    def evolution_error(cls, error: str, **kwargs):
        cls.log_with_emoji(
            "ERROR", "evolution_error", f"Erro Evolution: {error}", **kwargs
        )

    @classmethod
    def evolution_receive(cls, from_number: str, message_type: str, **kwargs):
        kwargs.update({"sender": from_number, "type": message_type})
        cls.log_with_emoji(
            "INFO",
            "evolution_receive",
            f"Recebido {message_type} de {from_number}",
            **kwargs,
        )

    @classmethod
    def webhook_receive(cls, endpoint: str, source: str, **kwargs):
        kwargs.update({"endpoint": endpoint, "source": source})
        cls.log_with_emoji(
            "INFO",
            "webhook_receive",
            f"Webhook recebido: {endpoint} de {source}",
            **kwargs,
        )

    @classmethod
    def webhook_process(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "webhook_process", message, **kwargs)

    @classmethod
    def system_start(cls, component: str, **kwargs):
        cls.log_with_emoji(
            "INFO", "system_start", f"Iniciando {component}", **kwargs
        )

    @classmethod
    def system_ready(cls, component: str, startup_time=None, **kwargs):
        if startup_time is not None and not isinstance(startup_time, str):
            try:
                kwargs["startup_ms"] = round(float(startup_time) * 1000, 2)
            except (ValueError, TypeError):
                pass
        cls.log_with_emoji(
            "INFO", "system_ready", f"{component} pronto", **kwargs
        )

    @classmethod
    def system_error(cls, component: str, error: str, **kwargs):
        kwargs["component"] = component
        cls.log_with_emoji(
            "ERROR", "system_error", f"Erro em {component}: {error}", **kwargs
        )

    @classmethod
    def system_warning(cls, message: str, **kwargs):
        cls.log_with_emoji("WARNING", "system_warning", message, **kwargs)

    @classmethod
    def system_info(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "system_info", message, **kwargs)

    @classmethod
    def system_debug(cls, message: str, **kwargs):
        cls.log_with_emoji("DEBUG", "system_debug", message, **kwargs)

    @classmethod
    def system_success(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "success", message, **kwargs)

    @classmethod
    def evolution_success(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "evolution_success", message, **kwargs)

    @classmethod
    def service_ready(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "success", f"Service: {message}", **kwargs)

    @classmethod
    def service_warning(cls, message: str, **kwargs):
        cls.log_with_emoji(
            "WARNING", "warning", f"Service: {message}", **kwargs
        )

    @classmethod
    def service_error(cls, message: str, **kwargs):
        cls.log_with_emoji("ERROR", "error", f"Service: {message}", **kwargs)

    @classmethod
    def service_info(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "info", f"Service: {message}", **kwargs)

    @classmethod
    def service_debug(cls, message: str, **kwargs):
        cls.log_with_emoji("DEBUG", "debug", f"Service: {message}", **kwargs)

    @classmethod
    def service_success(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "success", f"Service: {message}", **kwargs)

    @classmethod
    def model_error(cls, message: str, **kwargs):
        cls.log_with_emoji("ERROR", "error", f"Model: {message}", **kwargs)

    @classmethod
    def model_warning(cls, message: str, **kwargs):
        cls.log_with_emoji("WARNING", "warning", f"Model: {message}", **kwargs)

    @classmethod
    def multimodal_event(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "agentic_multimodal", message, **kwargs)

    @classmethod
    def calendar_event(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "team_calendar", message, **kwargs)

    @classmethod
    def followup_event(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "team_followup", message, **kwargs)

    @classmethod
    def conversation_event(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "agentic_response", message, **kwargs)

    @classmethod
    def conversation_success(cls, message: str, **kwargs):
        cls.log_with_emoji("INFO", "success", message, **kwargs)


EmojiLogger.setup_logger()
emoji_logger = EmojiLogger()

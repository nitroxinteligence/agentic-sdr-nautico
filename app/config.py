"""
Configurações centralizadas do SDR IA Náutico
"""
import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dotenv import load_dotenv
from pathlib import Path

# Carrega variáveis de ambiente
if not os.getenv('ENVIRONMENT') or os.getenv('ENVIRONMENT') == 'development':
    possible_paths = [
        Path(__file__).parent.parent / '.env',
        Path('/app/.env'),
        Path('.env'),
    ]

    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"✅ Arquivo .env encontrado: {env_path}")
            break
else:
    print("✅ Usando variáveis de ambiente do servidor (EasyPanel)")


class Settings(BaseSettings):
    """Configurações do sistema"""

    use_stateless_mode: bool = Field(
        default=False, env="USE_STATELESS_MODE"
    )
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    evolution_api_url: str = Field(env="EVOLUTION_API_URL")
    evolution_api_key: str = Field(env="EVOLUTION_API_KEY")
    evolution_instance_name: str = Field(env="EVOLUTION_INSTANCE_NAME")
    evolution_base_url: str = Field(default="", env="EVOLUTION_BASE_URL")
    evolution_instance: str = Field(default="", env="EVOLUTION_INSTANCE")
    supabase_url: str = Field(default="", env="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", env="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(default="", env="SUPABASE_SERVICE_KEY")
    supabase_db_url: str = Field(default="", env="SUPABASE_DB_URL")
    supabase_key: str = Field(default="", env="SUPABASE_KEY")
    redis_url: str = Field(
        default="redis://localhost:6379/0", env="REDIS_URL"
    )
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_username: str = Field(default="default", env="REDIS_USERNAME")
    redis_user: str = Field(default="default", env="REDIS_USER")  # Para compatibilidade EasyPanel
    google_auth_method: str = Field(
        default="oauth", env="GOOGLE_AUTH_METHOD"
    )
    google_oauth_client_id: str = Field(
        default="", env="GOOGLE_OAUTH_CLIENT_ID"
    )
    google_oauth_client_secret: str = Field(
        default="", env="GOOGLE_OAUTH_CLIENT_SECRET"
    )
    google_oauth_redirect_uri: str = Field(
        default="http://localhost:8000/google/callback",
        env="GOOGLE_OAUTH_REDIRECT_URI"
    )
    google_oauth_refresh_token: str = Field(
        default="", env="GOOGLE_OAUTH_REFRESH_TOKEN"
    )
    google_use_service_account: bool = Field(
        default=False, env="GOOGLE_USE_SERVICE_ACCOUNT"
    )
    google_service_account_email: str = Field(
        default="", env="GOOGLE_SERVICE_ACCOUNT_EMAIL"
    )
    google_private_key: str = Field(default="", env="GOOGLE_PRIVATE_KEY")
    google_project_id: str = Field(default="", env="GOOGLE_PROJECT_ID")
    google_private_key_id: str = Field(
        default="", env="GOOGLE_PRIVATE_KEY_ID"
    )
    google_client_id: str = Field(default="", env="GOOGLE_CLIENT_ID")
    google_calendar_id: str = Field(default="", env="GOOGLE_CALENDAR_ID")
    enable_google_calendar: bool = Field(
        default=False, env="ENABLE_GOOGLE_CALENDAR"
    )
    google_workspace_user_email: str = Field(
        default="", env="GOOGLE_WORKSPACE_USER_EMAIL"
    )
    kommo_client_id: str = Field(default="", env="KOMMO_CLIENT_ID")
    kommo_base_url: str = Field(
        default="https://api-c.kommo.com", env="KOMMO_BASE_URL"
    )
    kommo_client_secret: str = Field(default="", env="KOMMO_CLIENT_SECRET")
    kommo_subdomain: str = Field(default="", env="KOMMO_SUBDOMAIN")
    kommo_redirect_uri: str = Field(default="", env="KOMMO_REDIRECT_URI")
    kommo_pipeline_id: str = Field(default="", env="KOMMO_PIPELINE_ID")
    kommo_long_lived_token: str = Field(
        default="", env="KOMMO_LONG_LIVED_TOKEN"
    )
    kommo_access_token: str = Field(default="", env="KOMMO_ACCESS_TOKEN")
    human_intervention_pause_hours: int = Field(
        default=24, env="HUMAN_INTERVENTION_PAUSE_HOURS"
    )
    kommo_human_handoff_pipeline_id: str = Field(
        default="11672895", env="KOMMO_HUMAN_HANDOFF_PIPELINE_ID"
    )
    kommo_human_handoff_stage_id: int = Field(
        default=90421387, env="KOMMO_HUMAN_HANDOFF_STAGE_ID"
    )
    kommo_not_interested_stage_id: int = Field(
        default=89709599, env="KOMMO_NOT_INTERESTED_STAGE_ID"
    )
    kommo_meeting_scheduled_stage_id: int = Field(
        default=89709595, env="KOMMO_MEETING_SCHEDULED_STAGE_ID"
    )
    kommo_agent_user_id: int = Field(
        default=11031887, env="KOMMO_AGENT_USER_ID"
    )
    # Estágios específicos do Náutico
    kommo_em_qualificacao_stage_id: int = Field(
        default=89709590, env="KOMMO_EM_QUALIFICACAO_STAGE_ID"
    )
    kommo_qualificado_stage_id: int = Field(
        default=89709591, env="KOMMO_QUALIFICADO_STAGE_ID"
    )
    kommo_desqualificado_stage_id: int = Field(
        default=89709592, env="KOMMO_DESQUALIFICADO_STAGE_ID"
    )
    kommo_novo_lead_stage_id: int = Field(
        default=89709589, env="KOMMO_NOVO_LEAD_STAGE_ID"  
    )
    api_base_url: str = Field(
        default="http://localhost:8000", env="API_BASE_URL"
    )
    webhook_base_url: str = Field(
        default="http://localhost:8000", env="WEBHOOK_BASE_URL"
    )
    agente_response_delay_seconds: int = Field(
        default=2, env="AGENTE_RESPONSE_DELAY_SECONDS"
    )
    report_day_of_week: str = Field(
        default="monday", env="REPORT_DAY_OF_WEEK"
    )
    report_time: str = Field(default="09:00", env="REPORT_TIME")
    whatsapp_group_id: str = Field(default="", env="WHATSAPP_GROUP_ID")
    business_hours_start: str = Field(
        default="08:00", env="BUSINESS_HOURS_START"
    )
    business_hours_end: str = Field(
        default="18:00", env="BUSINESS_HOURS_END"
    )
    business_timezone: str = Field(
        default="America/Sao_Paulo", env="BUSINESS_TIMEZONE"
    )
    weekend_support: bool = Field(
        default=False, env="WEEKEND_SUPPORT"
    )
    followup_delay_30min: int = Field(
        default=30, env="FOLLOWUP_DELAY_30MIN"
    )
    followup_delay_4hours: int = Field(
        default=240, env="FOLLOWUP_DELAY_4HOURS"
    )
    followup_delay_24hours: int = Field(
        default=1440, env="FOLLOWUP_DELAY_24HOURS"
    )
    followup_delay_48hours: int = Field(
        default=2880, env="FOLLOWUP_DELAY_48HOURS"
    )
    max_follow_up_attempts: int = Field(
        default=4, env="MAX_FOLLOW_UP_ATTEMPTS", 
        description="Máximo de follow-ups por semana para um lead"
    )
    timezone: str = Field(default="America/Sao_Paulo", env="TIMEZONE")
    debug: bool = Field(default=False, env="DEBUG")
    debug_kommo: bool = Field(default=False, env="DEBUG_KOMMO")
    environment: str = Field(default="production", env="ENVIRONMENT")
    log_level: str = Field(default="INFO")
    agno_model: str = Field(default="gemini-2.5-pro")
    agno_fallback_model: str = Field(default="o1-mini")
    agno_max_tokens: int = Field(default=4096)
    agno_temperature: float = Field(default=0.7)
    agno_reasoning_enabled: bool = Field(default=True)
    max_message_length: int = Field(default=4096)
    webhook_timeout: int = Field(default=30)
    typing_simulation_delay: float = Field(default=2.0)
    max_follow_up_attempts: int = Field(default=3)
    enable_qualification_agent: bool = Field(
        default=True, env="ENABLE_QUALIFICATION_AGENT"
    )
    enable_calendar_agent: bool = Field(
        default=True, env="ENABLE_CALENDAR_AGENT"
    )
    enable_followup_agent: bool = Field(
        default=True, env="ENABLE_FOLLOWUP_AGENT"
    )
    enable_knowledge_agent: bool = Field(
        default=True, env="ENABLE_KNOWLEDGE_AGENT"
    )
    enable_crm_agent: bool = Field(default=True, env="ENABLE_CRM_AGENT")
    enable_bill_analyzer_agent: bool = Field(
        default=True, env="ENABLE_BILL_ANALYZER_AGENT"
    )
    enable_kommo_auto_sync: bool = Field(
        default=True, env="ENABLE_KOMMO_AUTO_SYNC"
    )
    enable_agentic_sdr: bool = Field(default=True, env="ENABLE_AGENTIC_SDR")
    enable_sdr_team: bool = Field(default=True, env="ENABLE_SDR_TEAM")
    enable_typing_simulation: bool = Field(
        default=True, env="ENABLE_TYPING_SIMULATION"
    )
    typing_duration_short: float = Field(
        default=2.0, env="TYPING_DURATION_SHORT"
    )
    typing_duration_medium: float = Field(
        default=3.5, env="TYPING_DURATION_MEDIUM"
    )
    typing_duration_long: float = Field(
        default=5.0, env="TYPING_DURATION_LONG"
    )
    typing_speed_chars_per_second: int = Field(
        default=50, env="TYPING_SPEED_CHARS_PER_SECOND"
    )
    
    # Configurações de Áudio
    initial_audio_url: str = Field(
        default="https://xxxx.supabase.co/storage/v1/object/public/documents/AUDIO-ENVIAR-NO-INICIO-DA-CONVERSA-2%20(1).mp3", 
        env="INITIAL_AUDIO_URL"
    )
    
    # Configurações de Follow-up (conforme novo prompt)
    followup_delay_30min: int = Field(default=30, env="FOLLOWUP_DELAY_30MIN")
    followup_delay_4hours: int = Field(default=240, env="FOLLOWUP_DELAY_4HOURS")  # 4h em minutos
    followup_delay_24hours: int = Field(default=1440, env="FOLLOWUP_DELAY_24HOURS")  # 24h em minutos
    followup_delay_48hours: int = Field(default=2880, env="FOLLOWUP_DELAY_48HOURS")  # 48h em minutos
    response_delay_min: float = Field(
        default=1.5, env="RESPONSE_DELAY_MIN"
    )
    response_delay_max: float = Field(
        default=3.0, env="RESPONSE_DELAY_MAX"
    )
    response_delay_thinking: float = Field(
        default=5.0, env="RESPONSE_DELAY_THINKING"
    )
    delay_between_messages: float = Field(
        default=1.5, env="DELAY_BETWEEN_MESSAGES"
    )
    delay_before_media: float = Field(default=2.0, env="DELAY_BEFORE_MEDIA")
    delay_after_media: float = Field(default=3.0, env="DELAY_AFTER_MEDIA")
    simulate_reading_time: bool = Field(
        default=False, env="SIMULATE_READING_TIME"
    )
    reading_speed_wpm: int = Field(default=200, env="READING_SPEED_WPM")
    response_time_variation: float = Field(
        default=0.3, env="RESPONSE_TIME_VARIATION"
    )
    enable_message_buffer: bool = Field(
        default=True, env="ENABLE_MESSAGE_BUFFER"
    )
    message_buffer_timeout: float = Field(
        default=10.0, env="MESSAGE_BUFFER_TIMEOUT"
    )
    enable_message_splitter: bool = Field(
        default=True, env="ENABLE_MESSAGE_SPLITTER"
    )
    message_max_length: int = Field(
        default=200, env="MESSAGE_MAX_LENGTH"
    )
    message_chunk_delay: float = Field(
        default=0.8, env="MESSAGE_CHUNK_DELAY"
    )
    message_add_indicators: bool = Field(
        default=False, env="MESSAGE_ADD_INDICATORS"
    )
    enable_smart_splitting: bool = Field(
        default=True, env="ENABLE_SMART_SPLITTING"
    )
    smart_splitting_fallback: bool = Field(
        default=True, env="SMART_SPLITTING_FALLBACK"
    )
    enable_context_analysis: bool = Field(
        default=True, env="ENABLE_CONTEXT_ANALYSIS"
    )
    enable_sentiment_analysis: bool = Field(
        default=True, env="ENABLE_SENTIMENT_ANALYSIS"
    )
    enable_emotional_triggers: bool = Field(
        default=True, env="ENABLE_EMOTIONAL_TRIGGERS"
    )
    enable_lead_scoring: bool = Field(
        default=True, env="ENABLE_LEAD_SCORING"
    )
    enable_multimodal_analysis: bool = Field(
        default=True, env="ENABLE_MULTIMODAL_ANALYSIS"
    )
    enable_bill_photo_analysis: bool = Field(
        default=True, env="ENABLE_BILL_PHOTO_ANALYSIS"
    )
    enable_voice_message_transcription: bool = Field(
        default=True, env="ENABLE_VOICE_MESSAGE_TRANSCRIPTION"
    )
    enable_auto_translation: bool = Field(
        default=False, env="ENABLE_AUTO_TRANSLATION"
    )
    enable_kommo_crm: bool = Field(
        default=False, env="ENABLE_KOMMO_CRM"
    )
    enable_knowledge_base: bool = Field(
        default=True, env="ENABLE_KNOWLEDGE_BASE"
    )
    enable_follow_up_automation: bool = Field(
        default=True, env="ENABLE_FOLLOW_UP_AUTOMATION"
    )
    enable_redis: bool = Field(
        default=True, env="ENABLE_REDIS"
    )
    enable_supabase: bool = Field(
        default=True, env="ENABLE_SUPABASE"
    )
    enable_evolution_api: bool = Field(
        default=True, env="ENABLE_EVOLUTION_API"
    )
    enable_emoji_usage: bool = Field(
        default=True, env="ENABLE_EMOJI_USAGE"
    )
    enable_audio_messages: bool = Field(
        default=False, env="ENABLE_AUDIO_MESSAGES"
    )
    enable_sticker_responses: bool = Field(
        default=False, env="ENABLE_STICKER_RESPONSES"
    )
    enable_reaction_messages: bool = Field(
        default=True, env="ENABLE_REACTION_MESSAGES"
    )
    min_qualification_score: int = Field(
        default=7, env="MIN_QUALIFICATION_SCORE"
    )
    auto_schedule_threshold: int = Field(
        default=9, env="AUTO_SCHEDULE_THRESHOLD"
    )
    bill_value_threshold: float = Field(
        default=200.0, env="BILL_VALUE_THRESHOLD"
    )
    auto_request_bill_photo: bool = Field(
        default=True, env="AUTO_REQUEST_BILL_PHOTO"
    )
    require_decision_maker: bool = Field(
        default=True, env="REQUIRE_DECISION_MAKER"
    )
    max_qualification_attempts: int = Field(
        default=3, env="MAX_QUALIFICATION_ATTEMPTS"
    )
    primary_ai_model: str = Field(
        default="gemini-2.5-pro", env="PRIMARY_AI_MODEL"
    )
    fallback_ai_model: str = Field(
        default="o3-mini", env="FALLBACK_AI_MODEL"
    )
    enable_model_fallback: bool = Field(
        default=True, env="ENABLE_MODEL_FALLBACK"
    )
    gemini_retry_attempts: int = Field(
        default=2, env="GEMINI_RETRY_ATTEMPTS"
    )
    gemini_retry_delay: float = Field(default=5.0, env="GEMINI_RETRY_DELAY")
    ai_max_tokens: int = Field(default=4096, env="AI_MAX_TOKENS")
    ai_temperature: float = Field(default=0.7, env="AI_TEMPERATURE")
    ai_top_p: float = Field(default=0.9, env="AI_TOP_P")
    ai_frequency_penalty: float = Field(
        default=0.1, env="AI_FREQUENCY_PENALTY"
    )
    enable_streaming_responses: bool = Field(
        default=True, env="ENABLE_STREAMING_RESPONSES"
    )
    enable_parallel_agent_processing: bool = Field(
        default=True, env="ENABLE_PARALLEL_AGENT_PROCESSING"
    )
    max_reasoning_depth: int = Field(default=3, env="MAX_REASONING_DEPTH")

    @validator('google_private_key')
    def process_private_key(cls, v):
        """Processa a chave privada do Google para formato correto"""
        if v:
            return v.replace('\n', '\n')
        return v

    def get_google_credentials(self) -> Dict[str, Any]:
        """Retorna credenciais do Google formatadas para autenticação"""
        return {
            "type": "service_account",
            "project_id": self.google_project_id,
            "private_key_id": self.google_private_key_id,
            "private_key": self.google_private_key,
            "client_email": self.google_service_account_email,
            "client_id": self.google_client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url":
                "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url":
                f"https://www.googleapis.com/robot/v1/metadata/x509/"
                f"{self.google_service_account_email}"
        }

    def get_redis_url(self) -> str:
        """Constrói a URL do Redis com autenticação se necessário"""
        # Se REDIS_URL está definida e não é a padrão, usar ela
        if self.redis_url and self.redis_url != "redis://localhost:6379/0":
            return self.redis_url
            
        # Construir URL a partir das credenciais individuais
        # Usar redis_user se definido, senão redis_username 
        username = self.redis_user if self.redis_user != "default" else self.redis_username
        
        if self.redis_password:
            return (
                f"redis://{username}:{self.redis_password}@"
                f"{self.redis_host}:{self.redis_port}/0"
            )
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    def get_postgres_url(self) -> str:
        """DESNECESSÁRIO - Não usamos PostgreSQL"""
        return ""

    def is_business_hours(self) -> bool:
        """Verifica se está dentro do horário comercial"""
        from datetime import datetime
        import pytz

        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        current_time = now.strftime("%H:%M")

        return (
            self.business_hours_start <= current_time <=
            self.business_hours_end
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


settings = Settings()

QUALIFICATION_STAGES = [
    "INITIAL_CONTACT", "IDENTIFYING_NEED", "QUALIFYING", "DISCOVERY",
    "PRESENTING_SOLUTION", "HANDLING_OBJECTIONS", "SCHEDULING", "FOLLOW_UP"
]
QUALIFICATION_STATUS = ["PENDING", "QUALIFIED", "NOT_QUALIFIED"]
SOLUTION_TYPES = [
    "USINA_PROPRIA", "USINA_TERRENO_PARCEIRO", "ASSINATURA_COMERCIAL",
    "ASSINATURA_RESIDENCIAL", "MERCADO_LIVRE", "MOBILIDADE_ELETRICA"
]
FOLLOW_UP_TYPES = [
    "IMMEDIATE_REENGAGEMENT", "DAILY_NURTURING", "MEETING_CONFIRMATION",
    "MEETING_REMINDER", "ABANDONMENT_CHECK", "CUSTOM"
]
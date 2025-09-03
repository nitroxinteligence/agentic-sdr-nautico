#!/usr/bin/env python3
"""
SDR IA Náutico - Aplicação Principal
Ponto de entrada da aplicação FastAPI
"""

import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importações dos módulos da aplicação
from app.config import settings
from app.utils.logger import emoji_logger
from app.integrations.redis_client import redis_client
from app.integrations.supabase_client import supabase_client
from app.services.message_buffer import get_message_buffer
from app.services.message_splitter import get_message_splitter
from app.services.followup_manager import followup_manager_service
from app.services.followup_service_100_real import FollowUpServiceReal
from app.services.conversation_monitor import get_conversation_monitor
from app.agents.agentic_sdr_stateless import AgenticSDRStateless

# Importações dos routers
from app.api.health import router as health_router
from app.api.webhooks import router as webhooks_router
from app.api.kommo_webhook import router as kommo_router
from app.api.google_auth import router as google_auth_router

# Variáveis globais para serviços
agentic_sdr = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    global agentic_sdr
    
    # Startup
    start_time = time.time()
    emoji_logger.system_start("SDR IA Náutico v0.3")
    
    try:
        # Conectar ao Redis (opcional em desenvolvimento)
        try:
            await redis_client.connect()
            if redis_client.redis_client:
                emoji_logger.system_ready("Redis", data={"url": redis_client.redis_url.split('@')[-1]})
            else:
                emoji_logger.system_warning("Redis não disponível - continuando sem cache")
        except Exception as e:
            emoji_logger.system_warning(f"Redis não disponível: {e} - continuando sem cache")
        
        # Testar conexão Supabase
        if await supabase_client.test_connection():
            emoji_logger.system_ready("Supabase")
        else:
            emoji_logger.system_error("Supabase", "Falha na conexão")
        
        # Inicializar Message Buffer com configurações corretas
        from app.services.message_buffer import set_message_buffer, MessageBuffer
        message_buffer = MessageBuffer(
            timeout=settings.message_buffer_timeout,
            max_size=10
        )
        set_message_buffer(message_buffer)
        emoji_logger.system_ready("Message Buffer", data={"timeout": f"{message_buffer.timeout}s"})
        
        # Inicializar Message Splitter com configurações corretas
        from app.services.message_splitter import set_message_splitter, MessageSplitter
        message_splitter = MessageSplitter(
            max_length=settings.message_max_length,
            add_indicators=settings.message_add_indicators,
            enable_smart_splitting=settings.enable_smart_splitting,
            smart_splitting_fallback=settings.smart_splitting_fallback
        )
        set_message_splitter(message_splitter)
        emoji_logger.system_ready("Message Splitter", data={"max_length": message_splitter.max_length})
        
        # Inicializar Conversation Monitor
        conversation_monitor = get_conversation_monitor()
        await conversation_monitor.initialize()
        emoji_logger.system_ready("Conversation Monitor")
        
        # Sistema refatorado pronto
        emoji_logger.system_ready("Sistema Refatorado", data={"modules": "Core + Services"})
        
        # Inicializar FollowUp Service
        followup_service = FollowUpServiceReal()
        emoji_logger.system_ready("FollowUp Service")
        
        # Inicializar AgenticSDR Stateless
        agentic_sdr = AgenticSDRStateless()
        await agentic_sdr.initialize()
        emoji_logger.system_ready("AgenticSDR (Stateless)", data={"status": "sistema pronto"})
        
        # FollowUp Services prontos
        emoji_logger.system_ready("FollowUp Services")
        
        # Aviso sobre workers de follow-up (se Redis disponível)
        if redis_client.redis_client:
            emoji_logger.system_info("📌 IMPORTANTE: Para follow-ups do Náutico funcionarem, execute: python start_workers.py")
            emoji_logger.system_info("📌 Os workers processam as filas do Redis para envio automatizado")
        
        # Pré-aquecer o sistema
        emoji_logger.system_info("🔥 Pré-aquecendo AgenticSDR (Stateless)...")
        warmup_agent = AgenticSDRStateless()
        await warmup_agent.initialize()
        
        # Sistema pronto
        startup_time = time.time() - start_time
        emoji_logger.system_ready("SDR IA Náutico", startup_time=startup_time)
        
        yield
        
    except Exception as e:
        emoji_logger.system_error("Startup", f"Erro durante startup: {e}")
        raise
    
    # Shutdown
    try:
        emoji_logger.info("🔄 Iniciando shutdown...")
        
        # Parar serviços
        if message_buffer:
            await message_buffer.shutdown()
        
        conversation_monitor = get_conversation_monitor()
        if conversation_monitor:
            await conversation_monitor.shutdown()
            
        # FollowUp Manager não precisa de shutdown
            
        if redis_client:
            await redis_client.disconnect()
            
        emoji_logger.info("✅ Shutdown concluído")
        
    except Exception as e:
        emoji_logger.error(f"Erro durante shutdown: {e}")

# Criar aplicação FastAPI
app = FastAPI(
    title="SDR IA Náutico",
    description="Sistema de IA para automação de vendas via WhatsApp",
    version="0.3.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health_router, tags=["health"])
app.include_router(webhooks_router, tags=["webhooks"])
app.include_router(kommo_router, tags=["kommo"])
app.include_router(google_auth_router, tags=["auth"])

# Endpoint raiz
@app.get("/")
async def root():
    """Endpoint raiz da aplicação"""
    return {
        "message": "SDR IA Náutico",
        "version": "0.3.0",
        "status": "running",
        "agent": "Marina Campelo"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )
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
            emoji_logger.system_warning(f"Redis connection failed: {e}")

        # Testar conexão com Supabase
        try:
            is_connected = await supabase_client.test_connection()
            if is_connected:
                emoji_logger.system_ready("Supabase")
            else:
                emoji_logger.system_warning("Supabase não disponível")
        except Exception as e:
            emoji_logger.system_warning(f"Supabase connection failed: {e}")

        # Inicializar Message Buffer (já inicializado no construtor)
        message_buffer = get_message_buffer()
        emoji_logger.system_ready("Message Buffer", data={"timeout": f"{message_buffer.timeout}s"})

        # Inicializar Message Splitter (já inicializado no construtor)
        message_splitter = get_message_splitter()
        emoji_logger.system_ready("Message Splitter", data={"max_length": message_splitter.max_length})

        # Inicializar Conversation Monitor
        conversation_monitor = get_conversation_monitor()
        await conversation_monitor.initialize()
        emoji_logger.system_ready("Conversation Monitor")

        # Inicializar sistema refatorado
        emoji_logger.system_ready("Sistema Refatorado", data={"modules": "Core + Services"})

        # FollowUp Services (já inicializado no construtor)
        emoji_logger.system_ready("FollowUp Service")

        # Inicializar Agente Principal
        agentic_sdr = AgenticSDRStateless()
        await agentic_sdr.initialize()
        emoji_logger.system_ready("AgenticSDR (Stateless)", data={"status": "sistema pronto"})

        # Inicializar FollowUp Services Final
        emoji_logger.system_ready("FollowUp Services")
        
        # Avisos importantes
        emoji_logger.system_info("📌 IMPORTANTE: Para follow-ups do Náutico funcionarem, execute: python start_workers.py")
        emoji_logger.system_info("📌 Os workers processam as filas do Redis para envio automatizado")

        # Pré-aquecimento desabilitado para debugging
        emoji_logger.system_info("🔥 Warmup desabilitado - servidor pronto para uso")

        elapsed = (time.time() - start_time) * 1000
        emoji_logger.system_ready("SDR IA Náutico", data={"startup_ms": elapsed})

        emoji_logger.system_info("🎯 Lifespan: Entrando no yield - servidor ativo")
        emoji_logger.system_info(f"🔍 Tasks ativas: {len(asyncio.all_tasks())}")
        
        yield
        
        emoji_logger.system_info("🎯 Lifespan: Saindo do yield - iniciando shutdown")
        emoji_logger.system_info(f"🔍 Tasks ativas no shutdown: {len(asyncio.all_tasks())}")

    except Exception as e:
        emoji_logger.system_error("Startup", f"Erro durante startup: {e}")
        raise
    
    # Shutdown
    try:
        emoji_logger.system_info("🔄 Iniciando shutdown...")
        
        # Parar serviços
        if 'message_buffer' in locals():
            await message_buffer.shutdown()
        
        conversation_monitor = get_conversation_monitor()
        if conversation_monitor:
            await conversation_monitor.shutdown()
            
        if redis_client:
            await redis_client.disconnect()
            
        emoji_logger.system_info("✅ Shutdown concluído")
        
    except Exception as e:
        emoji_logger.system_error("Shutdown", f"Erro durante shutdown: {e}")

# Criar aplicação FastAPI
app = FastAPI(
    title="SDR IA Náutico",
    description="Sistema de SDR IA para Clube Náutico Capibaribe",
    version="0.3.0",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(health_router)
app.include_router(webhooks_router)
app.include_router(kommo_router)
app.include_router(google_auth_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
#!/usr/bin/env python3
"""
Workers do Sistema de Follow-up - Náutico
Inicia os workers necessários para execução dos follow-ups via Redis
"""

import asyncio
import signal
import sys
from app.services.followup_executor_service import FollowUpSchedulerService
from app.services.followup_worker import FollowUpWorker
from app.utils.logger import emoji_logger
from app.integrations.redis_client import redis_client

class WorkerManager:
    """Gerenciador dos workers de follow-up"""
    
    def __init__(self):
        self.scheduler = FollowUpSchedulerService()
        self.worker = FollowUpWorker()
        self.running = False
    
    async def start(self):
        """Inicia todos os workers"""
        emoji_logger.system_start("Workers de Follow-up do Náutico")
        
        try:
            # Conectar ao Redis
            await redis_client.connect()
            if not redis_client.redis_client:
                raise Exception("Redis não conectado - workers não podem funcionar")
            
            emoji_logger.system_success("Redis conectado para workers")
            
            # Iniciar scheduler (enfileira tarefas)
            await self.scheduler.start()
            emoji_logger.system_ready("FollowUp Scheduler iniciado")
            
            # Iniciar worker (processa filas)
            await self.worker.start()
            emoji_logger.system_ready("FollowUp Worker iniciado")
            
            self.running = True
            emoji_logger.system_ready("Workers de Follow-up", data={"status": "operacional"})
            
        except Exception as e:
            emoji_logger.system_error("Worker Manager", f"Erro ao iniciar workers: {e}")
            raise
    
    async def stop(self):
        """Para todos os workers"""
        if not self.running:
            return
            
        emoji_logger.system_info("🔄 Parando workers de follow-up...")
        
        try:
            await self.scheduler.stop()
            await self.worker.stop()
            await redis_client.disconnect()
            
            self.running = False
            emoji_logger.system_success("Workers de follow-up parados")
            
        except Exception as e:
            emoji_logger.system_error("Worker Manager", f"Erro ao parar workers: {e}")
    
    def setup_signal_handlers(self):
        """Configura handlers para sinais de sistema"""
        def signal_handler(signum, frame):
            emoji_logger.system_info(f"Sinal {signum} recebido - parando workers...")
            asyncio.create_task(self.stop())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Função principal dos workers"""
    manager = WorkerManager()
    manager.setup_signal_handlers()
    
    try:
        await manager.start()
        
        # Loop principal - manter workers rodando
        while manager.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        emoji_logger.system_info("Interrupção do usuário - parando workers...")
    except Exception as e:
        emoji_logger.system_error("Worker Manager", f"Erro nos workers: {e}")
    finally:
        await manager.stop()
        sys.exit(0)

if __name__ == "__main__":
    emoji_logger.system_info("🚀 Iniciando Workers de Follow-up do Náutico...")
    asyncio.run(main())
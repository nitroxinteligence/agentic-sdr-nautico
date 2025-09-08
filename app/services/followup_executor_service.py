"""
FollowUp Scheduler Service - Enfileira Follow-ups para Execução
Este serviço agora APENAS enfileira tarefas no Redis, não as executa.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from app.integrations.supabase_client import SupabaseClient
from app.config import settings
from app.utils.logger import emoji_logger
from app.integrations.redis_client import redis_client
from loguru import logger


class FollowUpSchedulerService:
    """
    Serviço agendador de follow-ups.
    Verifica o banco de dados por follow-ups pendentes e os enfileira no Redis.
    """

    def __init__(self):
        self.db = SupabaseClient()
        self.redis = redis_client
        self.running = False
        self.check_interval = 60  # Aumentado de 15s para 60s para reduzir spam

    async def start(self):
        if self.running:
            logger.warning("Agendador de follow-ups já está rodando.")
            return
        self.running = True
        
        # Limpar follow-ups conflitantes na inicialização
        await self.cleanup_conflicting_followups()
        
        emoji_logger.system_ready("FollowUp Scheduler")
        asyncio.create_task(self._scheduling_loop())

    async def stop(self):
        self.running = False
        logger.info("Agendador de follow-ups parado.")

    async def _scheduling_loop(self):
        while self.running:
            try:
                await self.enqueue_pending_followups()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Erro no loop de agendamento: {e}")
                await asyncio.sleep(60)

    async def enqueue_pending_followups(self):
        """
        Busca follow-ups pendentes e os enfileira no Redis.
        """
        # Lock global para evitar múltiplas instâncias processando simultaneamente
        scheduler_lock = "followup_scheduler_lock"
        if not await self.redis.acquire_lock(scheduler_lock, ttl=120):  # 2 minutos
            logger.debug("Scheduler já em execução em outra instância - pulando")
            return
            
        try:
            now = datetime.now(timezone.utc)
            pending_followups = await self.db.get_pending_follow_ups()
            if not pending_followups:
                return
            logger.info(
                f"📋 {len(pending_followups)} follow-ups pendentes encontrados. Tempo atual: {now.isoformat()}"
            )
            
            # Debug: listar os follow-ups encontrados com seus horários
            for i, followup in enumerate(pending_followups[:5]):  # Mostrar apenas os 5 primeiros
                scheduled_at = followup.get('scheduled_at', 'N/A')
                followup_id = followup.get('id', 'N/A')
                lead_id = followup.get('lead_id', 'N/A')
                logger.info(f"🔍 Follow-up {i+1}: ID={followup_id}, Lead={lead_id}, Agendado={scheduled_at}")
            for followup in pending_followups:
                lead_id = followup.get('lead_id')
                followup_id = followup.get('id')
                
                # Verificar se já processamos este follow-up recentemente 
                recently_checked_key = f"followup_checked:{followup_id}"
                if await self.redis.get(recently_checked_key):
                    continue  # Pular, já verificamos recentemente
                    
                # Marcar como verificado por 5 minutos
                await self.redis.set(recently_checked_key, "1", ttl=300)
                
                if lead_id:
                    # Contar apenas follow-ups EXECUTADOS nas últimas 48 horas (não apenas criados)
                    two_days_ago = now - timedelta(hours=48)
                    count = await self.db.get_recent_followup_count(
                        lead_id, two_days_ago
                    )
                    logger.info(f"🔢 Lead {lead_id}: {count} follow-ups executados nas últimas 48h (limite: {settings.max_follow_up_attempts})")
                    
                    if count >= settings.max_follow_up_attempts:
                        followup_type = followup.get('type', 'UNKNOWN')
                        # Só log uma vez por follow-up específico, não spam
                        cancelled_key = f"followup_cancelled:{followup['id']}"
                        if not await self.redis.get(cancelled_key):
                            emoji_logger.system_warning(
                                f"🚫 Limite de follow-ups atingido para o lead {lead_id}. Tipo: {followup_type}, Count: {count}"
                            )
                            await self.redis.set(cancelled_key, "1", ttl=86400)  # 24h
                        else:
                            logger.debug(f"🔇 Follow-up {followup['id']} já teve warning de cancelamento logged")
                        
                        await self.db.update_follow_up_status(
                            followup['id'], 'cancelled'
                        )
                        continue
                lock_key = f"followup_enqueue:{followup['id']}"
                if await self.redis.acquire_lock(lock_key, ttl=60):
                    try:
                        task_payload = {
                            "task_type": "execute_followup",
                            "followup_id": followup['id'],
                            "lead_id": followup['lead_id'],
                            "phone_number": followup['phone_number'],
                            "followup_type": followup.get(
                                'follow_up_type', 'CUSTOM'
                            ),
                            "enqueued_at": now.isoformat()
                        }
                        await self.redis.enqueue("followup_tasks", task_payload)
                        await self.db.update_follow_up_status(
                            followup['id'], 'queued'
                        )
                        emoji_logger.followup_event(
                            f"✅ Follow-up {followup['id']} enfileirado para lead {followup['lead_id']} (agendado: {followup.get('scheduled_at')})"
                        )
                    except Exception as e:
                        logger.error(
                            f"❌ Erro ao enfileirar follow-up {followup['id']}: {e}"
                        )
                        await self.redis.release_lock(lock_key)
                else:
                    logger.warning(
                        f"⚠️ Follow-up {followup['id']} já está sendo processado."
                    )
        except Exception as e:
            logger.error(f"❌ Erro ao enfileirar follow-ups: {e}")

    async def force_enqueue_followups(self):
        """Força o enfileiramento imediato de follow-ups pendentes."""
        logger.info("🔄 Forçando enfileiramento de follow-ups...")
        await self.enqueue_pending_followups()
        logger.info("✅ Processo de enfileiramento concluído.")

    async def cleanup_conflicting_followups(self):
        """
        Remove follow-ups criados pelo sistema antigo (ConversationMonitor)
        que conflitam com o sistema principal do Náutico.
        """
        try:
            # Buscar TODOS os follow-ups pending - isso vai limpar tudo e resetar o sistema
            result = await asyncio.to_thread(
                self.db.client.table('follow_ups').select("*").eq('status', 'pending').execute
            )
            
            conflicting_followups = result.data or []
            
            if conflicting_followups:
                logger.info(f"🧹 LIMPEZA TOTAL: Encontrados {len(conflicting_followups)} follow-ups pending para cancelar")
                
                for followup in conflicting_followups:
                    await self.db.update_follow_up_status(
                        followup['id'], 'cancelled', 'Cancelado - reset sistema follow-up'
                    )
                    logger.info(f"🗑️ Follow-up cancelado: {followup['id']} (tipo: {followup.get('follow_up_type', 'N/A')})")
                    
                logger.info(f"✅ LIMPEZA TOTAL concluída: {len(conflicting_followups)} follow-ups cancelados")
                logger.info("🔄 Sistema resetado - novos follow-ups serão criados pelo FollowUpNauticoTools")
            else:
                logger.info("✅ Nenhum follow-up pending encontrado")
                
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de follow-ups conflitantes: {e}")

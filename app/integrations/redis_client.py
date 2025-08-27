"""
Redis Client - Cache e Filas
"""
import redis.asyncio as redis
import json
from typing import Optional, Any, List, Dict
from datetime import datetime
from loguru import logger
from app.config import settings
from app.utils.safe_conversions import safe_json_loads, safe_int_conversion


class RedisClient:
    """Cliente Redis para cache e filas"""

    def __init__(self):
        self.redis_url = settings.get_redis_url()
        self.redis_client = None
        self.default_ttl = 3600

    async def connect(self):
        """Conecta ao Redis com retry limitado"""
        import asyncio
        max_retries = 3  # Reduzido para desenvolvimento
        retry_delay = 1.0  # Reduzido para desenvolvimento
        for attempt in range(max_retries):
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=50
                )
                await self.redis_client.ping()
                logger.info(
                    f"✅ Conectado ao Redis: {self.redis_url.split('@')[-1]}"
                )
                return
            except Exception as e:
                error_msg = str(e)
                if "Error 8" in error_msg or "Name or service not known" in error_msg:
                    logger.warning(
                        f"⚠️ Redis host não encontrado (tentativa {attempt + 1})"
                    )
                else:
                    logger.warning(
                        f"⚠️ Erro ao conectar no Redis (tentativa {attempt + 1}): {e}"
                    )
                if attempt < max_retries - 1:
                    wait_time = retry_delay
                    logger.info(f"⏳ Aguardando {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.warning("⚠️ Redis não disponível - continuando sem cache")
                    self.redis_client = None

    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Desconectado do Redis")

    async def ping(self) -> bool:
        """Verifica se o Redis está acessível"""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if not self.redis_client:
            return None
        try:
            value = await self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Erro ao obter cache {key}: {e}")
            return None

    async def set(
            self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Define valor no cache"""
        if not self.redis_client:
            return False
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            if ttl is None:
                ttl = self.default_ttl
            await self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Erro ao definir cache {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove chave do cache"""
        if not self.redis_client:
            return False
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Erro ao deletar cache {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        if not self.redis_client:
            return False
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Erro ao verificar cache {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """Define TTL para chave existente"""
        if not self.redis_client:
            return False
        try:
            return await self.redis_client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Erro ao definir TTL {key}: {e}")
            return False

    async def get_ttl(self, key: str) -> int:
        """Obtém TTL restante de uma chave"""
        if not self.redis_client:
            return -1
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Erro ao obter TTL {key}: {e}")
            return -1

    async def cache_conversation(
        self, phone: str, conversation_data: Dict[str, Any], ttl: int = 7200
    ):
        """Cache de conversa"""
        key = f"conversation:{phone}"
        await self.set(key, conversation_data, ttl)

    async def get_conversation(self, phone: str) -> Optional[Dict[str, Any]]:
        """Obtém conversa do cache"""
        key = f"conversation:{phone}"
        return await self.get(key)

    async def cache_lead_info(
        self, phone: str, lead_data: Dict[str, Any], ttl: int = 86400
    ):
        """Cache de informações do lead"""
        key = f"lead:{phone}"
        await self.set(key, lead_data, ttl)

    async def get_lead_info(self, phone: str) -> Optional[Dict[str, Any]]:
        """Obtém informações do lead do cache"""
        key = f"lead:{phone}"
        return await self.get(key)

    async def enqueue(
            self, queue_name: str, data: Any, priority: int = 0
    ) -> bool:
        """Adiciona item à fila"""
        if not self.redis_client:
            return False
        try:
            payload = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "priority": priority
            }
            value = json.dumps(payload)
            if priority > 0:
                queue_key = f"queue:priority:{queue_name}"
                await self.redis_client.lpush(queue_key, value)
            else:
                queue_key = f"queue:{queue_name}"
                await self.redis_client.rpush(queue_key, value)
            logger.debug(f"Item adicionado à fila {queue_name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enfileirar em {queue_name}: {e}")
            return False

    async def dequeue(
        self, queue_name: str, timeout: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Remove item da fila"""
        if not self.redis_client:
            return None
        try:
            priority_key = f"queue:priority:{queue_name}"
            normal_key = f"queue:{queue_name}"
            value = await self.redis_client.lpop(priority_key)
            if not value:
                if timeout > 0:
                    result = await self.redis_client.blpop(normal_key, timeout)
                    if result:
                        value = result[1]
                else:
                    value = await self.redis_client.lpop(normal_key)
            if value:
                return safe_json_loads(value)
            return None
        except Exception as e:
            logger.error(f"Erro ao desenfileirar de {queue_name}: {e}")
            return None

    async def queue_size(self, queue_name: str) -> int:
        """Obtém tamanho da fila"""
        if not self.redis_client:
            return 0
        try:
            priority_key = f"queue:priority:{queue_name}"
            normal_key = f"queue:{queue_name}"
            priority_size = await self.redis_client.llen(priority_key)
            normal_size = await self.redis_client.llen(normal_key)
            return priority_size + normal_size
        except Exception as e:
            logger.error(f"Erro ao obter tamanho da fila {queue_name}: {e}")
            return 0

    async def enqueue_follow_up(
        self,
        phone: str,
        message: str,
        scheduled_at: datetime,
        follow_up_type: str
    ):
        """Enfileira follow-up"""
        data = {
            "phone": phone,
            "message": message,
            "scheduled_at": scheduled_at.isoformat(),
            "type": follow_up_type
        }
        await self.enqueue("follow_ups", data)

    async def enqueue_message(
            self, phone: str, message: str, priority: int = 0
    ):
        """Enfileira mensagem para envio"""
        data = {"phone": phone, "message": message, "type": "text"}
        await self.enqueue("messages", data, priority)

    async def check_rate_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> bool:
        """Verifica rate limit"""
        if not self.redis_client:
            return True
        try:
            rate_key = f"rate:{key}"
            current = await self.redis_client.incr(rate_key)
            if current == 1:
                await self.redis_client.expire(rate_key, window_seconds)
            return current <= max_requests
        except Exception as e:
            logger.error(f"Erro ao verificar rate limit {key}: {e}")
            return True

    async def get_rate_limit_remaining(
            self, key: str, max_requests: int
    ) -> int:
        """Obtém requisições restantes"""
        if not self.redis_client:
            return max_requests
        try:
            rate_key = f"rate:{key}"
            current = await self.redis_client.get(rate_key)
            if current:
                remaining = max_requests - safe_int_conversion(current)
                return max(0, remaining)
            return max_requests
        except Exception as e:
            logger.error(f"Erro ao obter rate limit {key}: {e}")
            return max_requests

    async def acquire_lock(self, key: str, ttl: int = 10) -> bool:
        """Adquire lock distribuído"""
        if not self.redis_client:
            return True
        try:
            lock_key = f"lock:{key}"
            result = await self.redis_client.set(
                lock_key, "1", nx=True, ex=ttl
            )
            return result is not None
        except Exception as e:
            logger.error(f"Erro ao adquirir lock {key}: {e}")
            return False

    async def release_lock(self, key: str) -> bool:
        """Libera lock"""
        try:
            lock_key = f"lock:{key}"
            return await self.delete(lock_key)
        except Exception as e:
            logger.error(f"Erro ao liberar lock {key}: {e}")
            return False

    async def publish(self, channel: str, message: Any):
        """Publica mensagem em canal"""
        if not self.redis_client:
            return
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            await self.redis_client.publish(channel, message)
            logger.debug(f"Mensagem publicada em {channel}")
        except Exception as e:
            logger.error(f"Erro ao publicar em {channel}: {e}")

    async def subscribe(self, channels: List[str]):
        """Inscreve em canais"""
        if not self.redis_client:
            return None
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(*channels)
            logger.info(f"Inscrito em canais: {channels}")
            return pubsub
        except Exception as e:
            logger.error(f"Erro ao inscrever em canais: {e}")
            return None

    async def set_human_handoff_pause(self, phone: str) -> bool:
        """Define uma pausa permanente para intervenção humana."""
        if not self.redis_client:
            return False
        try:
            key = f"lead:pause:{phone}"
            await self.redis_client.set(key, "1")
            logger.info(
                f"🤝 Handoff humano ativado para {phone}."
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao definir pausa handoff {phone}: {e}")
            return False

    async def is_human_handoff_active(self, phone: str) -> bool:
        """Verifica se há pausa ativa para intervenção humana"""
        if not self.redis_client:
            return False
        try:
            key = f"lead:pause:{phone}"
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Erro ao verificar pausa handoff {phone}: {e}")
            return False

    async def clear_human_handoff_pause(self, phone: str) -> bool:
        """Remove pausa de intervenção humana"""
        if not self.redis_client:
            return False
        try:
            key = f"lead:pause:{phone}"
            result = await self.redis_client.delete(key)
            if result > 0:
                logger.info(f"✅ Pausa handoff removida para {phone}")
            return result > 0
        except Exception as e:
            logger.error(f"Erro ao remover pausa handoff {phone}: {e}")
            return False

    async def increment_counter(
            self, counter_name: str, amount: int = 1
    ) -> int:
        """Incrementa contador"""
        if not self.redis_client:
            return 0
        try:
            key = f"counter:{counter_name}"
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Erro ao incrementar contador {counter_name}: {e}")
            return 0

    async def get_counter(self, counter_name: str) -> int:
        """Obtém valor do contador"""
        if not self.redis_client:
            return 0
        try:
            key = f"counter:{counter_name}"
            value = await self.redis_client.get(key)
            return safe_int_conversion(value, default=0)
        except Exception as e:
            logger.error(f"Erro ao obter contador {counter_name}: {e}")
            return 0

    async def reset_counter(self, counter_name: str):
        """Reseta contador"""
        key = f"counter:{counter_name}"
        await self.delete(key)

    async def save_session(
        self, session_id: str, data: Dict[str, Any], ttl: int = 3600
    ):
        """Salva sessão"""
        key = f"session:{session_id}"
        await self.set(key, data, ttl)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtém sessão"""
        key = f"session:{session_id}"
        return await self.get(key)

    async def extend_session(self, session_id: str, ttl: int = 3600):
        """Estende TTL da sessão"""
        key = f"session:{session_id}"
        await self.expire(key, ttl)

    async def end_session(self, session_id: str):
        """Encerra sessão"""
        key = f"session:{session_id}"
        await self.delete(key)


redis_client = RedisClient()
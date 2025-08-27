"""
Rate Limiter para APIs externas
Previne erro 429 (Too Many Requests)
"""

import asyncio
import time
from typing import Dict
from collections import deque


class RateLimiter:
    """
    Rate limiter com algoritmo Token Bucket
    """

    def __init__(
        self, max_requests: int = 10, time_window: int = 60, burst_size: int = 5
    ):
        self.max_requests = max_requests
        self.time_window = time_window
        self.burst_size = burst_size
        self.request_times = deque(maxlen=max_requests + burst_size)
        self.lock = asyncio.Lock()
        self.blocked_count = 0

    async def acquire(self, service_name: str = "API") -> bool:
        """
        Tenta adquirir permissão para fazer requisição
        """
        async with self.lock:
            now = time.time()
            while (self.request_times and
                   self.request_times[0] < now - self.time_window):
                self.request_times.popleft()
            if len(self.request_times) < self.max_requests:
                self.request_times.append(now)
                return True
            elif len(self.request_times) < self.max_requests + self.burst_size:
                self.request_times.append(now)
                print(f"⚠️ Rate Limiter: Usando burst para {service_name}")
                return True
            else:
                self.blocked_count += 1
                wait_time = self.request_times[0] + self.time_window - now
                print(
                    f"🚫 Rate Limiter: Bloqueando {service_name}. "
                    f"Aguarde {wait_time:.1f}s"
                )
                return False

    async def wait_if_needed(self, service_name: str = "API"):
        """
        Aguarda se necessário antes de fazer requisição
        """
        while not await self.acquire(service_name):
            async with self.lock:
                if self.request_times:
                    now = time.time()
                    wait_time = (
                        self.request_times[0] + self.time_window - now + 1
                    )
                    wait_time = max(1, min(wait_time, 10))
                else:
                    wait_time = 1
            print(
                f"⏳ Rate Limiter: Aguardando {wait_time:.1f}s para "
                f"{service_name}..."
            )
            await asyncio.sleep(wait_time)

    def get_stats(self) -> Dict:
        """Retorna estatísticas do rate limiter"""
        return {
            "current_requests": len(self.request_times),
            "max_requests": self.max_requests,
            "burst_size": self.burst_size,
            "blocked_count": self.blocked_count,
            "time_window": self.time_window
        }

    def reset(self):
        """Reseta o rate limiter"""
        self.request_times.clear()
        self.blocked_count = 0


class ServiceRateLimiters:
    """
    Gerenciador de rate limiters para múltiplos serviços
    """

    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
        self.default_configs = {
            "kommo": {"max_requests": 5, "time_window": 10, "burst_size": 2},
            "google": {"max_requests": 10, "time_window": 1, "burst_size": 5},
            "openai": {
                "max_requests": 50, "time_window": 60, "burst_size": 10
            },
            "evolution": {
                "max_requests": 30, "time_window": 60, "burst_size": 5
            },
            "supabase": {
                "max_requests": 100, "time_window": 60, "burst_size": 20
            }
        }

    def get_limiter(self, service: str) -> RateLimiter:
        """
        Obtém ou cria rate limiter para serviço
        """
        if service not in self.limiters:
            config = self.default_configs.get(
                service.lower(),
                {"max_requests": 10, "time_window": 60, "burst_size": 5}
            )
            self.limiters[service] = RateLimiter(**config)
        return self.limiters[service]

    async def wait_for_service(self, service: str):
        """
        Aguarda rate limit para serviço específico
        """
        limiter = self.get_limiter(service)
        await limiter.wait_if_needed(service)

    def get_all_stats(self) -> Dict[str, Dict]:
        """Retorna estatísticas de todos os limiters"""
        return {s: l.get_stats() for s, l in self.limiters.items()}

    def reset_all(self):
        """Reseta todos os rate limiters"""
        for limiter in self.limiters.values():
            limiter.reset()


rate_limiters = ServiceRateLimiters()


async def wait_for_kommo():
    """Aguarda rate limit do Kommo CRM"""
    await rate_limiters.wait_for_service("kommo")


async def wait_for_google():
    """Aguarda rate limit do Google APIs"""
    await rate_limiters.wait_for_service("google")


async def wait_for_openai():
    """Aguarda rate limit do OpenAI"""
    await rate_limiters.wait_for_service("openai")


async def wait_for_evolution():
    """Aguarda rate limit do Evolution API"""
    await rate_limiters.wait_for_service("evolution")


async def wait_for_supabase():
    """Aguarda rate limit do Supabase"""
    await rate_limiters.wait_for_service("supabase")

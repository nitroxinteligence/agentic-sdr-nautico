"""
Kommo CRM Queue Service
Handles all Kommo API requests through a queue system to respect rate limits
Maximum 7 requests per second, with proper backoff strategies
"""

import asyncio
import time
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from app.utils.logger import emoji_logger
from app.integrations.redis_client import redis_client
from app.services.crm_service_100_real import CRMServiceReal


class QueueOperationType(Enum):
    CREATE_LEAD = "create_lead"
    UPDATE_LEAD = "update_lead"
    UPDATE_STAGE = "update_stage"
    GET_LEAD_BY_PHONE = "get_lead_by_phone"
    GET_LEAD_BY_ID = "get_lead_by_id"
    ADD_NOTE = "add_note"
    CREATE_OR_UPDATE_LEAD = "create_or_update_lead"


@dataclass
class QueuedOperation:
    operation_type: QueueOperationType
    operation_data: Dict[str, Any]
    priority: int = 1  # 1 = highest priority, 5 = lowest
    created_at: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None
    result_event: Optional[asyncio.Event] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    operation_id: str = ""

    def __post_init__(self):
        if not self.operation_id:
            self.operation_id = f"{self.operation_type.value}_{int(time.time() * 1000)}"


class KommoQueueService:
    """
    Serviço de fila para operações do Kommo CRM
    Garante que não excedamos 7 requests por segundo
    """

    def __init__(self):
        self.crm_service = CRMServiceReal()
        self.request_queue: asyncio.Queue[QueuedOperation] = asyncio.Queue()
        self.processing = False
        self.request_history: List[float] = []
        self.max_requests_per_second = 6  # Mantém margem de segurança (doc = 7)
        self.blocked_until = 0.0
        self.consecutive_429_errors = 0
        self.consecutive_403_errors = 0
        self.stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "rate_limited": 0,
            "ip_blocked": 0,
            "queue_size": 0
        }

    async def initialize(self):
        """Inicializa o serviço de fila e o CRM service"""
        await self.crm_service.initialize()
        if not self.processing:
            asyncio.create_task(self._process_queue())
            self.processing = True
            emoji_logger.service_ready("🚀 Kommo Queue Service iniciado")

    def _can_make_request(self) -> bool:
        """
        Verifica se podemos fazer uma requisição baseado no rate limit
        Implementa a regra dos 7 requests por segundo
        """
        current_time = time.time()

        # Se estamos bloqueados, aguardar
        if current_time < self.blocked_until:
            return False

        # Remove requisições antigas (mais de 1 segundo)
        self.request_history = [
            req_time for req_time in self.request_history
            if current_time - req_time < 1.0
        ]

        # Verifica se podemos fazer mais uma requisição
        return len(self.request_history) < self.max_requests_per_second

    def _register_request(self):
        """Registra uma nova requisição no histórico"""
        self.request_history.append(time.time())

    async def _wait_for_rate_limit(self):
        """Aguarda até poder fazer próxima requisição"""
        while not self._can_make_request():
            current_time = time.time()

            # Se estamos bloqueados, aguardar o tempo de bloqueio
            if current_time < self.blocked_until:
                wait_time = self.blocked_until - current_time
                emoji_logger.service_warning(f"⏳ IP bloqueado - aguardando {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                continue

            # Calcular tempo de espera baseado na requisição mais antiga
            if self.request_history:
                oldest_request = min(self.request_history)
                wait_time = 1.0 - (current_time - oldest_request) + 0.1  # +0.1s de margem
                if wait_time > 0:
                    emoji_logger.service_info(f"⏳ Rate limit - aguardando {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)

    def _handle_rate_limit_response(self, status_code: int):
        """Trata respostas relacionadas ao rate limit"""
        current_time = time.time()

        if status_code == 429:
            self.consecutive_429_errors += 1
            self.stats["rate_limited"] += 1
            # Aumenta o tempo de bloqueio progressivamente
            block_time = min(5 * self.consecutive_429_errors, 60)  # Máximo 60s
            self.blocked_until = current_time + block_time
            emoji_logger.service_warning(
                f"🚫 HTTP 429 - Rate limit excedido. Bloqueando por {block_time}s"
            )

        elif status_code == 403:
            self.consecutive_403_errors += 1
            self.stats["ip_blocked"] += 1
            # IP foi bloqueado - aguardar mais tempo
            block_time = min(30 * self.consecutive_403_errors, 300)  # Máximo 5min
            self.blocked_until = current_time + block_time
            emoji_logger.service_error(
                f"🚨 HTTP 403 - IP bloqueado! Aguardando {block_time}s"
            )
        else:
            # Reset contadores em caso de sucesso
            self.consecutive_429_errors = 0
            self.consecutive_403_errors = 0

    async def _execute_operation(self, operation: QueuedOperation) -> Dict[str, Any]:
        """Executa uma operação específica do CRM"""
        try:
            # Aguardar rate limit
            await self._wait_for_rate_limit()

            # Registrar requisição
            self._register_request()

            # Executar operação baseada no tipo
            if operation.operation_type == QueueOperationType.CREATE_LEAD:
                result = await self.crm_service.create_lead(operation.operation_data)

            elif operation.operation_type == QueueOperationType.UPDATE_LEAD:
                lead_id = operation.operation_data.pop("lead_id")
                result = await self.crm_service.update_lead(lead_id, operation.operation_data)

            elif operation.operation_type == QueueOperationType.UPDATE_STAGE:
                lead_id = operation.operation_data["lead_id"]
                stage_name = operation.operation_data["stage_name"]
                notes = operation.operation_data.get("notes", "")
                phone_number = operation.operation_data.get("phone_number")
                result = await self.crm_service.update_lead_stage(
                    lead_id, stage_name, notes, phone_number
                )

            elif operation.operation_type == QueueOperationType.GET_LEAD_BY_PHONE:
                phone = operation.operation_data["phone"]
                result = await self.crm_service.get_lead_by_phone(phone)
                if result:
                    result = {"success": True, "lead": result}
                else:
                    result = {"success": False, "message": "Lead not found"}

            elif operation.operation_type == QueueOperationType.GET_LEAD_BY_ID:
                lead_id = operation.operation_data["lead_id"]
                result = await self.crm_service.get_lead_by_id(lead_id)
                if result:
                    result = {"success": True, "lead": result}
                else:
                    result = {"success": False, "message": "Lead not found"}

            elif operation.operation_type == QueueOperationType.ADD_NOTE:
                lead_id = operation.operation_data["lead_id"]
                note_text = operation.operation_data["note_text"]
                result = await self.crm_service.add_note_to_lead(lead_id, note_text)

            elif operation.operation_type == QueueOperationType.CREATE_OR_UPDATE_LEAD:
                result = await self.crm_service.create_or_update_lead(operation.operation_data)

            else:
                raise ValueError(f"Tipo de operação desconhecido: {operation.operation_type}")

            # Reset contadores de erro em caso de sucesso
            self.consecutive_429_errors = 0
            self.consecutive_403_errors = 0

            return result

        except Exception as e:
            # Verificar se é erro de rate limit
            error_str = str(e)
            if "429" in error_str:
                self._handle_rate_limit_response(429)
            elif "403" in error_str:
                self._handle_rate_limit_response(403)

            emoji_logger.service_error(f"Erro ao executar operação {operation.operation_type}: {e}")
            raise

    async def _process_queue(self):
        """Processa a fila de operações do Kommo"""
        emoji_logger.service_info("🔄 Iniciando processamento da fila Kommo")

        while True:
            try:
                # Aguarda operação na fila (com timeout para permitir estatísticas)
                try:
                    operation = await asyncio.wait_for(
                        self.request_queue.get(), timeout=30.0
                    )
                except asyncio.TimeoutError:
                    # Atualiza estatísticas a cada 30s quando não há operações
                    self.stats["queue_size"] = self.request_queue.qsize()
                    continue

                self.stats["total_operations"] += 1
                self.stats["queue_size"] = self.request_queue.qsize()

                try:
                    # Executar a operação
                    result = await self._execute_operation(operation)

                    # Salvar resultado
                    operation.result = result
                    self.stats["successful_operations"] += 1

                    emoji_logger.team_crm(
                        f"✅ Operação {operation.operation_type.value} concluída "
                        f"(ID: {operation.operation_id[:8]})"
                    )

                except Exception as e:
                    operation.error = e
                    operation.retry_count += 1

                    # Tentar novamente se ainda temos tentativas
                    if operation.retry_count <= operation.max_retries:
                        # Calcular delay de retry (backoff exponencial)
                        retry_delay = min(2 ** operation.retry_count, 60)  # Max 60s

                        emoji_logger.service_warning(
                            f"🔄 Reprocessando operação {operation.operation_type.value} "
                            f"em {retry_delay}s (tentativa {operation.retry_count}/{operation.max_retries})"
                        )

                        # Reagendar operação com delay
                        asyncio.create_task(
                            self._requeue_operation(operation, retry_delay)
                        )
                    else:
                        # Falha definitiva
                        self.stats["failed_operations"] += 1
                        emoji_logger.service_error(
                            f"❌ Operação {operation.operation_type.value} falhou definitivamente: {e}"
                        )

                # Notificar resultado se há event
                if operation.result_event:
                    operation.result_event.set()

                # Executar callback se existe
                if operation.callback:
                    try:
                        await operation.callback(operation)
                    except Exception as e:
                        emoji_logger.service_warning(f"Erro no callback: {e}")

            except Exception as e:
                emoji_logger.service_error(f"Erro no processamento da fila: {e}")
                await asyncio.sleep(5)  # Pausa antes de continuar

    async def _requeue_operation(self, operation: QueuedOperation, delay: float):
        """Reagenda uma operação após delay"""
        await asyncio.sleep(delay)
        await self.request_queue.put(operation)

    async def enqueue_operation(
        self,
        operation_type: QueueOperationType,
        operation_data: Dict[str, Any],
        priority: int = 1,
        wait_for_result: bool = False,
        callback: Optional[Callable] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Enfileira uma operação do Kommo CRM

        Args:
            operation_type: Tipo da operação
            operation_data: Dados para a operação
            priority: Prioridade (1 = alta, 5 = baixa)
            wait_for_result: Se True, aguarda o resultado
            callback: Função callback opcional

        Returns:
            Resultado da operação se wait_for_result=True
        """
        operation = QueuedOperation(
            operation_type=operation_type,
            operation_data=operation_data.copy(),
            priority=priority,
            callback=callback
        )

        if wait_for_result:
            operation.result_event = asyncio.Event()

        await self.request_queue.put(operation)

        emoji_logger.service_info(
            f"📋 Operação {operation_type.value} adicionada à fila "
            f"(ID: {operation.operation_id[:8]}, Fila: {self.request_queue.qsize()})"
        )

        if wait_for_result:
            # Aguarda resultado com timeout
            try:
                await asyncio.wait_for(operation.result_event.wait(), timeout=120.0)
                if operation.error:
                    raise operation.error
                return operation.result
            except asyncio.TimeoutError:
                raise asyncio.TimeoutError(
                    f"Timeout aguardando resultado da operação {operation_type.value}"
                )

        return None

    # Métodos de conveniência para cada tipo de operação
    async def create_lead(
        self,
        lead_data: Dict[str, Any],
        priority: int = 1,
        wait_for_result: bool = True
    ) -> Dict[str, Any]:
        """Cria um lead no Kommo via fila"""
        return await self.enqueue_operation(
            QueueOperationType.CREATE_LEAD,
            lead_data,
            priority,
            wait_for_result
        )

    async def update_lead(
        self,
        lead_id: str,
        update_data: Dict[str, Any],
        priority: int = 1,
        wait_for_result: bool = True
    ) -> Dict[str, Any]:
        """Atualiza um lead no Kommo via fila"""
        data = update_data.copy()
        data["lead_id"] = lead_id
        return await self.enqueue_operation(
            QueueOperationType.UPDATE_LEAD,
            data,
            priority,
            wait_for_result
        )

    async def update_lead_stage(
        self,
        lead_id: str,
        stage_name: str,
        notes: str = "",
        phone_number: Optional[str] = None,
        priority: int = 1,
        wait_for_result: bool = True
    ) -> Dict[str, Any]:
        """Atualiza o estágio de um lead no Kommo via fila"""
        data = {
            "lead_id": lead_id,
            "stage_name": stage_name,
            "notes": notes,
            "phone_number": phone_number
        }
        return await self.enqueue_operation(
            QueueOperationType.UPDATE_STAGE,
            data,
            priority,
            wait_for_result
        )

    async def get_lead_by_phone(
        self,
        phone: str,
        priority: int = 2,
        wait_for_result: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Busca lead por telefone via fila"""
        result = await self.enqueue_operation(
            QueueOperationType.GET_LEAD_BY_PHONE,
            {"phone": phone},
            priority,
            wait_for_result
        )
        return result.get("lead") if result and result.get("success") else None

    async def get_lead_by_id(
        self,
        lead_id: str,
        priority: int = 2,
        wait_for_result: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Busca lead por ID via fila"""
        result = await self.enqueue_operation(
            QueueOperationType.GET_LEAD_BY_ID,
            {"lead_id": lead_id},
            priority,
            wait_for_result
        )
        return result.get("lead") if result and result.get("success") else None

    async def add_note_to_lead(
        self,
        lead_id: str,
        note_text: str,
        priority: int = 3,
        wait_for_result: bool = False
    ) -> Dict[str, Any]:
        """Adiciona nota a um lead via fila"""
        return await self.enqueue_operation(
            QueueOperationType.ADD_NOTE,
            {"lead_id": lead_id, "note_text": note_text},
            priority,
            wait_for_result
        )

    async def create_or_update_lead(
        self,
        lead_data: Dict[str, Any],
        priority: int = 1,
        wait_for_result: bool = True
    ) -> Dict[str, Any]:
        """Cria ou atualiza lead via fila"""
        return await self.enqueue_operation(
            QueueOperationType.CREATE_OR_UPDATE_LEAD,
            lead_data,
            priority,
            wait_for_result
        )

    def get_queue_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da fila"""
        self.stats["queue_size"] = self.request_queue.qsize()
        self.stats["requests_in_last_second"] = len(self.request_history)
        self.stats["can_make_request"] = self._can_make_request()
        self.stats["blocked_until"] = self.blocked_until
        self.stats["consecutive_429_errors"] = self.consecutive_429_errors
        self.stats["consecutive_403_errors"] = self.consecutive_403_errors
        return self.stats.copy()

    async def close(self):
        """Fecha o serviço de fila"""
        self.processing = False
        await self.crm_service.close()
        emoji_logger.service_info("🛑 Kommo Queue Service encerrado")


# Instância global do serviço de fila
kommo_queue_service = KommoQueueService()
"""
Message Buffer Service - Simples e eficiente usando asyncio.Queue
"""
import asyncio
from typing import Dict, List, Optional
from loguru import logger
from app.utils.logger import emoji_logger


def validate_phone_number(phone: str) -> bool:
    """
    Valida se um número de telefone é válido
    - Deve ter entre 10 e 15 dígitos
    - Deve conter apenas números
    - Não deve ser números obviamente inválidos (muito longos ou curtos demais)
    """
    if not phone:
        return False
    
    # Remover caracteres não numéricos para validação
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # Validações básicas
    if len(digits_only) < 10 or len(digits_only) > 15:
        emoji_logger.system_warning(f"Message Buffer - Número inválido (tamanho): '{phone}' -> {len(digits_only)} dígitos")
        return False
    
    # Números obviamente inválidos (sequências muito longas de mesmo dígito)
    if len(set(digits_only)) < 3:  # Menos de 3 dígitos únicos
        emoji_logger.system_warning(f"Message Buffer - Número inválido (pouca variação): '{phone}'")
        return False
    
    # Números brasileiros válidos devem começar com 55 ou ter pelo menos 10 dígitos locais
    if digits_only.startswith('55') and len(digits_only) < 12:
        emoji_logger.system_warning(f"Message Buffer - Número brasileiro inválido: '{phone}' -> {len(digits_only)} dígitos")
        return False
    
    return True


class MessageBuffer:
    """
    Buffer inteligente - processa imediatamente se agente está livre,
    só aguarda timeout se agente está ocupado processando
    """

    def __init__(self, timeout: float = 10.0, max_size: int = 10):
        """
        Inicializa o buffer
        """
        self.timeout = timeout
        self.max_size = max_size
        self.queues: Dict[str, asyncio.Queue] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.processing_locks: Dict[str, asyncio.Lock] = {}
        emoji_logger.system_info(
            f"Buffer Inteligente inicializado (timeout={timeout}s, max={max_size})"
        )

    async def add_message(
            self, phone: str, content: str, message_data: Dict, media_data: Optional[Dict] = None
    ) -> None:
        """
        Adiciona mensagem ao buffer com validação de número
        """
        # Validar número de telefone antes de processar
        if not validate_phone_number(phone):
            emoji_logger.system_error(
                f"Message Buffer - Número de telefone inválido ignorado: '{phone}'"
            )
            return
        
        if phone not in self.queues:
            self.queues[phone] = asyncio.Queue(maxsize=self.max_size)
        
        # Só cria uma nova task se não existir uma ativa para este telefone
        if phone not in self.tasks or self.tasks[phone].done():
            self.tasks[phone] = asyncio.create_task(self._process_queue(phone))
            emoji_logger.system_debug(
                f"Nova task de processamento criada para {phone}"
            )
        
        message = {"content": content, "data": message_data, "media_data": media_data}
        try:
            self.queues[phone].put_nowait(message)
            emoji_logger.system_debug(
                f"Mensagem adicionada ao buffer para {phone} (task ativa: {not self.tasks[phone].done()})"
            )
        except asyncio.QueueFull:
            emoji_logger.system_warning(f"Buffer para {phone} cheio. O processamento ocorrerá em breve.")

    async def _process_queue(self, phone: str) -> None:
        """
        Processa a fila de forma simplificada e robusta.
        """
        if phone not in self.processing_locks:
            self.processing_locks[phone] = asyncio.Lock()
        
        queue = self.queues.get(phone)
        if not queue:
            return

        try:
            async with self.processing_locks[phone]:
                messages = []
                try:
                    # Aguarda a primeira mensagem
                    first_msg = await asyncio.wait_for(queue.get(), timeout=self.timeout)
                    if first_msg:
                        messages.append(first_msg)
                        emoji_logger.system_debug(f"Primeira mensagem recebida para {phone}, aguardando mensagens adicionais...")
                    
                    # Aguarda um período adicional para capturar mensagens sequenciais
                    # Usa o timeout configurado para capturar mensagens relacionadas
                    end_time = asyncio.get_event_loop().time() + self.timeout
                    
                    while asyncio.get_event_loop().time() < end_time:
                        try:
                            # Aguarda por mais mensagens com timeout curto
                            remaining_time = end_time - asyncio.get_event_loop().time()
                            if remaining_time <= 0:
                                break
                            
                            msg = await asyncio.wait_for(queue.get(), timeout=min(remaining_time, 1.0))
                            if msg:
                                messages.append(msg)
                                emoji_logger.system_debug(f"Mensagem adicional capturada para {phone} (total: {len(messages)})")
                        except asyncio.TimeoutError:
                            # Timeout normal - verifica se há mais mensagens na fila
                            while not queue.empty():
                                try:
                                    msg = queue.get_nowait()
                                    if msg:
                                        messages.append(msg)
                                except asyncio.QueueEmpty:
                                    break
                            break
                
                except asyncio.TimeoutError:
                    # Se não houver mensagens após o timeout inicial, a lista estará vazia.
                    pass

                if messages:
                    await self._process_messages(phone, messages)

        except Exception as e:
            emoji_logger.system_error("Message Buffer", f"Erro ao processar queue para {phone}: {e}")
        finally:
            # Limpa apenas a task para este telefone
            # Mantém queue e lock para futuras mensagens
            self.tasks.pop(phone, None)

    async def _process_messages(
            self, phone: str, messages: List[Dict]
    ) -> None:
        """
        Processa mensagens acumuladas de forma robusta.
        """
        from app.api.webhooks import process_message_with_agent

        if not messages:
            emoji_logger.system_warning("Buffer tentou processar um lote de mensagens vazio.", phone=phone)
            return

        # Filtro de segurança para remover quaisquer Nones que possam ter entrado na lista
        valid_messages = [m for m in messages if m and isinstance(m, dict)]
        if not valid_messages:
            emoji_logger.system_warning("Buffer processou um lote de mensagens inválido após a filtragem.", original_count=len(messages))
            return

        combined_content = "\n".join([msg.get("content", "") for msg in valid_messages if msg.get("content")] )
        emoji_logger.system_info(
                f"🔄 Processando {len(valid_messages)} mensagens combinadas para {phone} (total: {len(combined_content)} chars)"
            )
        # Correção: Usar repr() para exibir o conteúdo de forma segura, incluindo escapes.
        emoji_logger.system_debug(f"Conteúdo combinado para {phone}: {repr(combined_content)}")
        
        last_message_obj = valid_messages[-1]
        last_message_data = last_message_obj.get("data")
        media_data = last_message_obj.get("media_data")

        # Verificação de segurança para garantir que a carga útil da última mensagem exista
        if not last_message_data or not isinstance(last_message_data, dict):
            emoji_logger.system_error(
                "Message Buffer",
                "O campo 'data' da última mensagem no buffer é inválido ou None. Abortando processamento.",
                last_message_obj=last_message_obj
            )
            return

        message_id = last_message_data.get("key", {}).get("id", "")
        
        await process_message_with_agent(
            phone=phone,
            message_content=combined_content,
            original_message=last_message_data,
            message_id=message_id,
            media_data=media_data
        )

    async def shutdown(self) -> None:
        """Cancela todas as tasks ativas e limpa recursos"""
        for task in self.tasks.values():
            task.cancel()
        if self.tasks:
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)
        self.queues.clear()
        self.tasks.clear()
        self.processing_locks.clear()


message_buffer: Optional[MessageBuffer] = None


def get_message_buffer() -> MessageBuffer:
    """Retorna instância global do buffer"""
    global message_buffer
    if not message_buffer:
        message_buffer = MessageBuffer()
    return message_buffer


def set_message_buffer(buffer: MessageBuffer) -> None:
    """Define instância global do buffer"""
    global message_buffer
    message_buffer = buffer
"""
Evolution API Client - Integração com WhatsApp
"""
import httpx
import asyncio
import base64
import random
import time
import hashlib
import hmac
from typing import Optional, Dict, Any, List
from urllib.parse import quote
from loguru import logger
from app.utils.logger import emoji_logger
from tenacity import retry, stop_after_attempt, wait_exponential
from tenacity import retry_if_exception_type
from app.config import settings
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


class EvolutionAPIClient:
    """Cliente para integração com Evolution API v2 com conexão robusta"""

    def __init__(self):
        self.base_url = settings.evolution_api_url
        self.instance_name = settings.evolution_instance_name
        self.api_key = settings.evolution_api_key
        self._client = None
        self._last_health_check = 0
        self._health_check_interval = 30
        self._connection_failed = False
        self._circuit_breaker_reset_time = 0
        self._circuit_breaker_failure_count = 0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = 60

    def _create_client(self) -> httpx.AsyncClient:
        """Cria cliente HTTP com configuração otimizada"""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "apikey": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(
                connect=5.0, read=30.0, write=10.0, pool=5.0
            ),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=30.0
            ),
            http2=True,
            follow_redirects=True
        )

    @property
    def client(self) -> httpx.AsyncClient:
        """Retorna o cliente HTTP, criando se necessário"""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _check_circuit_breaker(self):
        """Verifica estado do circuit breaker"""
        if self._circuit_breaker_failure_count >= self._circuit_breaker_threshold:
            if time.time() < self._circuit_breaker_reset_time:
                raise Exception(
                    f"Circuit breaker ativo. Tentativas bloqueadas por "
                    f"{int(self._circuit_breaker_reset_time - time.time())}s"
                )
            else:
                self._circuit_breaker_failure_count = 0
                emoji_logger.system_info("Circuit breaker resetado")

    def _record_success(self):
        """Registra sucesso na conexão"""
        self._circuit_breaker_failure_count = 0
        self._connection_failed = False

    def _record_failure(self):
        """Registra falha na conexão"""
        self._circuit_breaker_failure_count += 1
        if self._circuit_breaker_failure_count >= self._circuit_breaker_threshold:
            self._circuit_breaker_reset_time = (
                time.time() + self._circuit_breaker_timeout
            )
            emoji_logger.system_error(
                "Evolution API",
                f"Circuit breaker ativado por {self._circuit_breaker_timeout}s "
                f"após {self._circuit_breaker_failure_count} falhas"
            )
        self._connection_failed = True

    async def health_check(self) -> bool:
        """Verifica saúde da conexão com Evolution API"""
        try:
            current_time = time.time()
            if current_time - self._last_health_check < self._health_check_interval:
                return not self._connection_failed
            await self._check_circuit_breaker()
            response = await self._make_request(
                "get",
                f"/instance/connectionState/{self.instance_name}",
                timeout=5.0
            )
            if response.status_code == 200:
                self._last_health_check = current_time
                self._record_success()
                return True
            else:
                self._record_failure()
                return False
        except Exception as e:
            logger.debug(f"Health check falhou: {e}")
            self._record_failure()
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError)
        )
    )
    async def _make_request(
            self, method: str, path: str, **kwargs
    ) -> httpx.Response:
        """Método base para fazer requisições com retry"""
        try:
            await self._check_circuit_breaker()
            if self._connection_failed:
                if self._client:
                    await self._client.aclose()
                self._client = self._create_client()
                emoji_logger.system_info("Reconectando ao Evolution API...")
            response = await getattr(self.client, method)(path, **kwargs)
            response.raise_for_status()  # Levanta exceção para status de erro
            self._record_success()
            return response
        except httpx.RequestError as e:
            self._record_failure()
            emoji_logger.system_error(
                "Evolution API",
                f"Erro de requisição para {e.request.method} {e.request.url}: {e}"
            )
            raise
        except httpx.HTTPStatusError as e:
            self._record_failure()
            emoji_logger.system_error(
                "Evolution API",
                f"Erro de status {e.response.status_code} para {e.request.method} {e.request.url}: {e.response.text}"
            )
            raise
        except Exception as e:
            self._record_failure()
            emoji_logger.system_error(
                "Evolution API",
                f"Erro inesperado na requisição {method.upper()} {path}: {e}"
            )
            raise

    async def create_instance(self) -> Dict[str, Any]:
        """Cria uma nova instância no Evolution API"""
        try:
            payload = {
                "instanceName": self.instance_name,
                "token": self.api_key,
                "qrcode": True,
                "integration": "WEBWHOOKS",
                "webhook_url": (
                    f"{settings.webhook_base_url}/webhooks/evolution"
                ),
                "webhook_by_events": True,
                "webhook_base64": True
            }
            response = await self._make_request(
                "post", "/instance/create", json=payload
            )
            emoji_logger.system_success(
                f"Instância {self.instance_name} criada"
            )
            return response.json()
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao criar instância: {e}")
            raise

    async def get_instance_info(self) -> Dict[str, Any]:
        """Obtém informações da instância"""
        try:
            response = await self._make_request(
                "get", f"/instance/connectionState/{self.instance_name}"
            )
            return response.json()
        except Exception as e:
            emoji_logger.system_error(
                "Evolution API",
                f"Erro ao obter info da instância: {e}"
            )
            raise

    async def connect_instance(self) -> Dict[str, Any]:
        """Conecta a instância gerando QR Code"""
        try:
            response = await self._make_request(
                "get", f"/instance/connect/{self.instance_name}"
            )
            data = response.json()
            if "qrcode" in data:
                emoji_logger.system_success("QR Code gerado")
                emoji_logger.system_debug(f"QR Code: {data['qrcode'][:50]}...")
            return data
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao conectar instância: {e}")
            raise

    async def disconnect_instance(self) -> Dict[str, Any]:
        """Desconecta a instância"""
        try:
            response = await self._make_request(
                "delete", f"/instance/logout/{self.instance_name}"
            )
            return response.json()
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao desconectar instância: {e}")
            raise

    async def send_text_message(
        self,
        phone: str,
        message: str,
        delay: Optional[float] = None,
        simulate_typing: bool = True
    ) -> Dict[str, Any]:
        """
        Envia mensagem de texto com timing humanizado
        """
        try:
            phone = self._format_phone(phone)
            if delay is None:
                is_complex = len(message) > 300 or "?" in message
                if is_complex:
                    delay = settings.response_delay_thinking
                else:
                    delay = random.uniform(
                        settings.response_delay_min,
                        settings.response_delay_max
                    )
            if delay > 0:
                await asyncio.sleep(delay)
            if simulate_typing:
                typing_duration = self._calculate_humanized_typing_duration(
                    len(message)
                )
                await self.send_typing(
                    phone, len(message),
                    duration_seconds=typing_duration,
                    context="agent_response"
                )
                emoji_logger.system_debug(
                    f"Aguardando {typing_duration:.1f}s de typing"
                )
                await asyncio.sleep(typing_duration)
            payload = {
                "number": phone,
                "text": message,
                "delay": int(settings.delay_between_messages * 1000)
            }
            response = await self._make_request(
                "post", f"/message/sendText/{self.instance_name}", json=payload
            )
            if response.status_code not in [200, 201]:
                error_text = response.text
                emoji_logger.system_error(
                    "Evolution API",
                    f"Evolution API retornou erro {response.status_code}: "
                    f"{error_text}"
                )
                raise Exception(
                    f"Erro ao enviar mensagem: Status {response.status_code} - "
                    f"{error_text}"
                )
            result = response.json()
            if not result.get("key", {}).get("id"):
                emoji_logger.system_error(
                    "Evolution API",
                    f"Mensagem não enviada - sem ID na resposta: {result}"
                )
                raise Exception(
                    "Mensagem não foi enviada - resposta inválida da API"
                )
            emoji_logger.system_info(
                f"Evolution API - Mensagem de texto enviada para {phone} (tamanho: {len(message)}, delay: {round(delay, 2)}s)"
            )
            emoji_logger.system_debug(f"Resposta da Evolution API: {result}")
            return result
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao enviar mensagem: {e}")
            raise

    def _calculate_humanized_typing_duration(
            self, message_length: int
    ) -> float:
        """
        Calcula uma duração de "typing" humanizada
        """
        if message_length > 500:
            base_duration = 12.0
        elif message_length > 250:
            base_duration = 8.0
        elif message_length > 150:
            base_duration = 5.0
        elif message_length > 50:
            base_duration = 3.0
        else:
            base_duration = 2.0
        variation = base_duration * 0.15
        duration = base_duration + random.uniform(-variation, variation)
        return max(1.0, min(duration, 15.0))

    async def send_typing(
        self,
        phone: str,
        message_length: int = 0,
        duration_seconds: Optional[float] = None,
        context: str = "unknown"
    ):
        """
        Simula digitação com timing dinâmico
        """
        from app.services.typing_controller import (
            typing_controller, TypingContext
        )
        context_map = {
            "agent_response": TypingContext.AGENT_RESPONSE,
            "user_message": TypingContext.USER_MESSAGE,
            "system_message": TypingContext.SYSTEM_MESSAGE,
            "media_upload": TypingContext.MEDIA_UPLOAD,
            "unknown": TypingContext.SYSTEM_MESSAGE
        }
        typing_context = context_map.get(
            context, TypingContext.SYSTEM_MESSAGE
        )
        decision = typing_controller.should_show_typing(
            typing_context, message_length
        )
        if not decision.should_show:
            logger.debug(f"Typing não será mostrado: {decision.reason}")
            return
        try:
            phone = self._format_phone(phone)
            if not duration_seconds:
                duration = decision.duration or 2.0
            else:
                duration = duration_seconds
            
            # Payload corrigido para o padrão da Evolution API
            payload = {
                "number": phone,
                "presence": "composing",
                "delay": int(duration * 1000)
            }
            
            # Endpoint corrigido para 'sendPresence'
            await self._make_request(
                "post",
                f"/chat/sendPresence/{self.instance_name}",
                json=payload
            )
            emoji_logger.system_info(
                f"Evolution API - Typing enviado para {phone} (duração: {round(duration, 2)}s, tamanho: {message_length})"
            )
            logger.debug(f"Typing enviado por {duration}s")
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao simular digitação: {e}")
            logger.debug(f"Digitação falhou mas continuando: {e}")

    async def send_reaction(self, phone: str, message_id: str, emoji: str):
        """
        Envia reação a uma mensagem
        """
        try:
            phone = self._format_phone(phone)
            payload = {
                "key": {
                    "remoteJid": f"{phone}@s.whatsapp.net",
                    "fromMe": False,
                    "id": message_id
                },
                "reaction": emoji
            }
            response = await self._make_request(
                "post",
                f"/message/sendReaction/{self.instance_name}",
                json=payload
            )
            if response.status_code not in [200, 201]:
                error_text = response.text
                emoji_logger.system_error(
                    "Evolution API",
                    f"Evolution API retornou erro {response.status_code}: "
                    f"{error_text}"
                )
                raise Exception(
                    f"Erro ao enviar reação: Status {response.status_code} - "
                    f"{error_text}"
                )
            result = response.json()
            if not result.get("key", {}).get("id"):
                emoji_logger.system_error(
                    "Evolution API",
                    f"Reação não enviada - sem ID na resposta: {result}"
                )
                raise Exception(
                    "Reação não foi enviada - resposta inválida da API"
                )
            emoji_logger.system_info(
                f"Evolution API - Reação '{emoji}' enviada. ID: {result.get('key', {}).get('id', 'N/A')}"
            )
            return result
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao enviar reação: {e}")
            raise

    async def send_reply(
        self,
        phone: str,
        message_id: str,
        text: str,
        simulate_typing: bool = True
    ) -> Dict[str, Any]:
        """
        Envia uma resposta citando uma mensagem anterior
        """
        try:
            phone = self._format_phone(phone)
            if simulate_typing:
                typing_duration = self._calculate_humanized_typing_duration(
                    len(text)
                )
                await self.send_typing(
                    phone, len(text),
                    duration_seconds=typing_duration,
                    context="agent_response"
                )
                emoji_logger.system_debug(
                    f"Aguardando {typing_duration:.1f}s de typing"
                )
                await asyncio.sleep(typing_duration)
            payload = {
                "number": phone,
                "text": text,
                "options": {
                    "quoted": {
                        "key": {
                            "remoteJid": f"{phone}@s.whatsapp.net",
                            "id": message_id
                        }
                    }
                }
            }
            response = await self._make_request(
                "post", f"/message/sendText/{self.instance_name}", json=payload
            )
            if response.status_code not in [200, 201]:
                error_text = response.text
                emoji_logger.system_error(
                    "Evolution API",
                    f"Evolution API retornou erro {response.status_code}: "
                    f"{error_text}"
                )
                raise Exception(
                    f"Erro ao enviar resposta: Status {response.status_code} - "
                    f"{error_text}"
                )
            result = response.json()
            if not result.get("key", {}).get("id"):
                emoji_logger.system_error(
                    "Evolution API",
                    f"Resposta não enviada - sem ID na resposta: {result}"
                )
                raise Exception(
                    "Resposta não foi enviada - resposta inválida da API"
                )
            emoji_logger.system_info(
                f"Evolution API - Resposta enviada para {phone} (tamanho: {len(text)})"
            )
            return result
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao enviar resposta: {e}")
            raise

    async def send_image(
        self,
        phone: str,
        image_path: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia imagem
        """
        try:
            phone = self._format_phone(phone)
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            payload = {
                "number": phone,
                "mediatype": "image",
                "media": f"data:image/jpeg;base64,{image_data}"
            }
            if caption:
                payload["caption"] = caption
            response = await self._make_request(
                "post",
                f"/message/sendMedia/{self.instance_name}",
                json=payload
            )
            emoji_logger.system_info(
                f"Evolution API - Imagem enviada para {phone}"
            )
            return response.json()
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao enviar imagem: {e}")
            raise

    async def send_document(
        self,
        phone: str,
        document_path: str,
        filename: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia documento (PDF, etc)
        """
        try:
            phone = self._format_phone(phone)
            with open(document_path, "rb") as f:
                doc_data = base64.b64encode(f.read()).decode()
            payload = {
                "number": phone,
                "mediatype": "document",
                "media": f"data:application/pdf;base64,{doc_data}",
                "fileName": filename
            }
            if caption:
                payload["caption"] = caption
            response = await self._make_request(
                "post",
                f"/message/sendMedia/{self.instance_name}",
                json=payload
            )
            emoji_logger.system_info(
                f"Evolution API - Documento enviado para {phone}"
            )
            return response.json()
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao enviar documento: {e}")
            raise

    async def send_audio(
        self,
        phone: str,
        audio_path: str,
        as_voice_note: bool = True
    ) -> Dict[str, Any]:
        """
        Envia áudio
        """
        try:
            phone = self._format_phone(phone)
            with open(audio_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode()
            payload = {
                "number": phone,
                "mediatype": "audio",
                "media": f"data:audio/mpeg;base64,{audio_data}",
                "ptt": as_voice_note
            }
            response = await self._make_request(
                "post",
                f"/message/sendMedia/{self.instance_name}",
                json=payload
            )
            emoji_logger.system_info(
                f"Evolution API - Áudio enviado para {phone}"
            )
            return response.json()
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao enviar áudio: {e}")
            raise

    async def get_all_chats(self) -> List[Dict[str, Any]]:
        """Obtém todos os chats"""
        try:
            response = await self._make_request(
                "get", f"/chat/findChats/{self.instance_name}"
            )
            return response.json()
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Erro ao obter chats: {e}")
            raise

    async def get_messages(
        self,
        phone: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Obtém mensagens de um chat
        """
        try:
            phone = self._format_phone(phone)
            response = await self._make_request(
                "post",
                f"/chat/findMessages/{self.instance_name}",
                json={
                    "where": {
                        "remoteJid": f"{phone}@s.whatsapp.net"
                    },
                    "limit": limit
                }
            )
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter mensagens: {e}")
            raise

    async def mark_as_read(self, phone: str, message_id: str):
        """
        Marca mensagem como lida
        """
        try:
            phone = self._format_phone(phone)
            payload = {
                "read_messages": [
                    {
                        "remoteJid": f"{phone}@s.whatsapp.net",
                        "id": message_id
                    }
                ]
            }
            await self._make_request(
                "post",
                f"/chat/markMessageAsRead/{self.instance_name}",
                json=payload
            )
            logger.debug(f"Mensagem {message_id} marcada como lida")
        except Exception as e:
            logger.error(f"Erro ao marcar como lida: {e}")

    async def get_profile_picture(self, phone: str) -> Optional[str]:
        """
        Obtém foto de perfil
        """
        try:
            phone = self._format_phone(phone)
            response = await self._make_request(
                "post",
                f"/chat/fetchProfilePictureUrl/{self.instance_name}",
                json={"number": phone}
            )
            data = response.json()
            return data.get("profilePictureUrl")
        except Exception as e:
            logger.error(f"Erro ao obter foto de perfil: {e}")
            return None

    async def get_business_profile(
            self, phone: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtém perfil business
        """
        try:
            phone = self._format_phone(phone)
            response = await self._make_request(
                "post",
                f"/chat/fetchBusinessProfile/{self.instance_name}",
                json={"number": phone}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter perfil business: {e}")
            return None

    async def setup_webhook(self, webhook_url: str):
        """
        Configura webhook para receber eventos
        """
        try:
            payload = {
                "webhook": {
                    "enabled": True,
                    "url": webhook_url,
                    "webhookByEvents": True,
                    "webhookBase64": True
                },
                "events": [
                    "APPLICATION_STARTUP", "QRCODE_UPDATED",
                    "CONNECTION_UPDATE", "MESSAGES_SET", "MESSAGES_UPSERT",
                    "MESSAGES_UPDATE", "MESSAGES_DELETE", "SEND_MESSAGE",
                    "CONTACTS_SET", "CONTACTS_UPSERT", "CONTACTS_UPDATE",
                    "PRESENCE_UPDATE", "CHATS_SET", "CHATS_UPSERT",
                    "CHATS_UPDATE", "CHATS_DELETE", "GROUPS_UPSERT",
                    "GROUPS_UPDATE", "GROUP_PARTICIPANTS_UPDATE",
                    "NEW_JWT_TOKEN"
                ]
            }
            response = await self._make_request(
                "post", f"/webhook/set/{self.instance_name}", json=payload
            )
            logger.info(f"Webhook configurado: {webhook_url}")
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao configurar webhook: {e}")
            raise

    async def get_webhook(self) -> Dict[str, Any]:
        """Obtém configuração atual do webhook"""
        try:
            response = await self._make_request(
                "get", f"/webhook/get/{self.instance_name}"
            )
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter webhook: {e}")
            raise

    async def send_text_to_group(
        self,
        group_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Envia mensagem para grupo
        """
        try:
            payload = {"number": group_id, "text": message}
            response = await self._make_request(
                "post", f"/message/sendText/{self.instance_name}", json=payload
            )
            logger.info(f"Mensagem enviada para grupo {group_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para grupo: {e}")
            raise

    async def get_group_info(self, group_id: str) -> Dict[str, Any]:
        """
        Obtém informações do grupo
        """
        try:
            response = await self._make_request(
                "post",
                f"/group/findGroupByJid/{self.instance_name}",
                json={"groupJid": group_id}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter info do grupo: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=1, max=30),
        retry=retry_if_exception_type(
            (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)
        )
    )
    async def get_media_as_base64(self, message_key: Dict[str, Any]) -> Optional[str]:
        """
        Busca a mídia de uma mensagem diretamente em base64 usando a chave da mensagem.
        Implementa retry com backoff exponencial para lidar com timeouts da Evolution API.
        """
        if not message_key:
            emoji_logger.system_warning("Message key vazia fornecida para get_media_as_base64")
            return None
        
        try:
            payload = {"message": {"key": message_key}}
            emoji_logger.system_info(f"Evolution API: Tentando obter mídia em base64 para key: {message_key}")
            
            response = await self._make_request(
                "post",
                f"/chat/getBase64FromMediaMessage/{self.instance_name}",
                json=payload
            )
            
            if response.status_code in [200, 201]:  # Aceita 200 (OK) e 201 (Created)
                result = response.json()
                base64_data = result.get("base64")
                if base64_data:
                    emoji_logger.system_success("Mídia em base64 obtida com sucesso")
                    return base64_data
                else:
                    emoji_logger.system_warning("Resposta da API não contém dados base64")
                    return None
            elif response.status_code == 400:
                # Erro 400 específico - pode ser AggregateError
                error_text = response.text
                emoji_logger.system_error(
                    "Evolution API",
                    f"Erro 400 da Evolution API (possível AggregateError): {error_text}"
                )
                # Para erro 400, não fazemos retry - é um erro de dados
                raise httpx.HTTPStatusError(
                    f"Bad Request: {error_text}", 
                    request=response.request, 
                    response=response
                )
            else:
                emoji_logger.system_error(
                    "Evolution API",
                    f"Erro ao buscar mídia em base64: {response.status_code} - {response.text}"
                )
                # Para outros códigos de erro, fazemos retry
                response.raise_for_status()
                return None
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # Não faz retry para erro 400
                emoji_logger.system_error("Evolution API", f"Erro 400 definitivo: {e}")
                return None
            else:
                # Re-raise para outros códigos para permitir retry
                emoji_logger.system_warning(f"Erro HTTP que será retentado: {e}")
                raise
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
            # Estes erros serão retentados automaticamente pelo decorador @retry
            emoji_logger.system_warning(f"Erro de rede que será retentado: {e}")
            raise
        except Exception as e:
            emoji_logger.system_error("Evolution API", f"Exceção inesperada ao buscar mídia em base64: {e}")
            return None

    def _format_phone(self, phone: str) -> str:
        """
        Formata número de telefone
        """
        phone = ''.join(filter(str.isdigit, phone))
        if not phone.startswith('55'):
            phone = '55' + phone
        return phone

    def decrypt_whatsapp_media(
        self,
        encrypted_data: bytes,
        media_key_base64: str,
        media_type: str = "image"
    ) -> Optional[bytes]:
        """
        Descriptografa mídia do WhatsApp usando AES-256-CBC
        """
        try:
            media_key = base64.b64decode(media_key_base64)
            logger.info(f"MediaKey decodificada: {len(media_key)} bytes")
            info_map = {
                "image": b"WhatsApp Image Keys",
                "video": b"WhatsApp Video Keys",
                "audio": b"WhatsApp Audio Keys",
                "document": b"WhatsApp Document Keys",
                "sticker": b"WhatsApp Image Keys"
            }
            info = info_map.get(media_type, b"WhatsApp Image Keys")
            hkdf = HKDF(
                algorithm=hashes.SHA256(), length=112, salt=None,
                info=info, backend=default_backend()
            )
            expanded_key = hkdf.derive(media_key)
            iv = expanded_key[:16]
            cipher_key = expanded_key[16:48]
            mac_key = expanded_key[48:80]
            logger.info(
                f"IV: {len(iv)} bytes, Cipher Key: {len(cipher_key)} bytes, "
                f"MAC Key: {len(mac_key)} bytes"
            )
            if len(encrypted_data) <= 10:
                logger.error("Dados criptografados muito pequenos")
                return None
            ciphertext = encrypted_data[:-10]
            mac_tag = encrypted_data[-10:]
            computed_mac = hmac.new(
                mac_key, iv + ciphertext, hashlib.sha256
            ).digest()[:10]
            if mac_tag != computed_mac:
                logger.warning(
                    f"MAC não corresponde - esperado: {mac_tag.hex()}, "
                    f"calculado: {computed_mac.hex()}"
                )
            cipher = Cipher(
                algorithms.AES(cipher_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            if len(decrypted_data) > 0:
                padding_length = decrypted_data[-1]
                if padding_length > 0 and padding_length <= 16:
                    if all(
                        b == padding_length
                        for b in decrypted_data[-padding_length:]
                    ):
                        decrypted_data = decrypted_data[:-padding_length]
            logger.info(
                f"Mídia descriptografada com sucesso: "
                f"{len(decrypted_data)} bytes"
            )
            return decrypted_data
        except Exception as e:
            logger.error(f"Erro ao descriptografar mídia: {e}")
            logger.exception(e)
            return None

    async def download_media(
            self, message_data: Dict[str, Any], media_type: str = "image"
    ) -> Optional[bytes]:
        """
        Baixa e descriptografa mídia de uma mensagem do WhatsApp
        """
        try:
            emoji_logger.system_info(f"Iniciando download_media para tipo: {media_type}")
            
            media_url = message_data.get("mediaUrl") or message_data.get("url")
            if not media_url:
                emoji_logger.system_error("Evolution Media", f"URL da mídia não encontrada nos dados. Dados: {list(message_data.keys())}")
                return None
                
            media_key = message_data.get("mediaKey")
            emoji_logger.system_info(f"Baixando mídia de: {media_url[:50]}... - MediaKey presente: {bool(media_key)}")
            
            if media_key:
                emoji_logger.system_info(
                    f"MediaKey presente - mídia será descriptografada (tipo: {media_type}) - MediaKey length: {len(media_key) if isinstance(media_key, str) else 'N/A'}"
                )
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                follow_redirects=True,
                limits=httpx.Limits(max_connections=5)
            ) as client:
                headers = {"User-Agent": "WhatsApp/2.23.0", "Accept": "*/*"}
                response = await client.get(media_url, headers=headers)
                if response.status_code == 200:
                    content = response.content
                    emoji_logger.system_success(
                        f"Mídia baixada com sucesso: {len(content)} bytes - Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'N/A')}"
                    )
                    
                    if media_key:
                        emoji_logger.system_info("Iniciando descriptografia da mídia...")
                        decrypted_content = self.decrypt_whatsapp_media(
                            encrypted_data=content,
                            media_key_base64=media_key,
                            media_type=media_type
                        )
                        if decrypted_content:
                            emoji_logger.system_success(
                                f"Mídia descriptografada com sucesso: {len(decrypted_content)} bytes - Redução de tamanho: {len(content) - len(decrypted_content)} bytes"
                            )
                            return decrypted_content
                        else:
                            emoji_logger.system_error("Evolution Media", "Falha na descriptografia da mídia")
                            emoji_logger.system_warning("Retornando mídia criptografada como fallback")
                            return content
                    else:
                        emoji_logger.system_info("Mídia não criptografada, retornando conteúdo original")
                        return content
                else:
                    emoji_logger.system_error(
                        "Evolution Media",
                        f"Erro HTTP ao baixar mídia: {response.status_code} - URL: {media_url[:50]}..., Headers: {dict(response.headers)}"
                    )
                    return None
        except httpx.TimeoutException as e:
            emoji_logger.system_error(
                "Evolution Media",
                f"Timeout ao baixar mídia - URL: {media_url[:50]}..., Erro: {str(e)}"
            )
            return None
        except httpx.RequestError as e:
            emoji_logger.system_error("Evolution Media", f"Erro de requisição ao baixar mídia: {e} - URL: {media_url[:50]}...")
            return None
        except Exception as e:
            emoji_logger.system_error("Evolution Media", f"Erro inesperado ao baixar mídia: {e} - Tipo: {type(e).__name__}")
            logger.exception(e)
            return None

    async def check_number_exists(self, phone: str) -> bool:
        """
        Verifica se número existe no WhatsApp
        """
        try:
            phone = self._format_phone(phone)
            response = await self._make_request(
                "post",
                f"/chat/checkNumber/{self.instance_name}",
                json={"number": phone}
            )
            data = response.json()
            return data.get("exists", False)
        except Exception as e:
            logger.error(f"Erro ao verificar número: {e}")
            return False

    async def close(self):
        """Fecha conexão do cliente"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def connect(self):
        """Conecta e verifica a instância"""
        try:
            info = await self.get_instance_info()
            if info.get("state") != "open":
                logger.info("Instância não conectada, gerando QR Code...")
                await self.connect_instance()
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            return False

    async def test_connection(self) -> bool:
        """Testa a conexão com a Evolution API"""
        try:
            info = await self.get_instance_info()
            return info.get("state") == "open"
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False


evolution_client = EvolutionAPIClient()
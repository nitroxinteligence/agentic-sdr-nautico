"""
Model Manager - Gerenciamento simples de modelos AI
ZERO complexidade, máxima confiabilidade
"""

from typing import Optional, Dict, Any
import asyncio
import base64
from app.utils.logger import emoji_logger
from app.config import settings

# Import das bibliotecas REAIS de AI
try:
    import google.generativeai as genai
    from google.api_core.exceptions import ResourceExhausted
    GEMINI_AVAILABLE = True
except ImportError:
    emoji_logger.system_warning("google-generativeai não instalado")
    GEMINI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# Classes wrapper para APIs REAIS
class Gemini:
    """Wrapper REAL para Gemini API"""
    def __init__(self, id, api_key):
        self.id = id
        self.api_key = api_key
        self.base_model_name = id
        if id == "gemini-1.5-pro":
            self.base_model_name = "gemini-1.5-pro"
        elif id == "gemini-2.0-flash-thinking":
            self.base_model_name = "gemini-1.5-flash"

        if GEMINI_AVAILABLE:
            genai.configure(api_key=api_key)

    async def achat(self, messages, system_prompt: Optional[str] = None):
        """Chamada REAL para Gemini API com suporte multimodal, criando um modelo com o system_prompt a cada chamada."""
        if not GEMINI_AVAILABLE:
            return type('Response', (), {'content': 'Gemini não disponível. Configure GOOGLE_API_KEY.'})()

        # Cria uma nova instância do modelo a cada chamada, garantindo que o system_prompt seja aplicado.
        model = genai.GenerativeModel(
            model_name=self.base_model_name,
            system_instruction=system_prompt
        )

        gemini_history = []
        for msg in messages:
            role = 'user' if msg['role'] == 'user' else 'model'
            content = msg.get('content', '')
            
            parts = []
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        parts.append(item.get("text", ""))
                    elif item.get("type") == "media":
                        media_data = item.get("media_data", {})
                        mime_type = media_data.get("mime_type")
                        base64_content = media_data.get("content")
                        if mime_type and base64_content:
                            parts.append({
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": base64.b64decode(base64_content)
                                }
                            })
            else:
                parts.append(str(content))

            if parts:
                gemini_history.append({'role': role, 'parts': parts})

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.generate_content(gemini_history)
        )

        try:
            # Acesso seguro ao conteúdo da resposta
            content = response.text
            return type('Response', (), {'content': content})()
        except Exception as e:
            # Se response.text falhar (e.g., sem 'parts' válidas), loga e retorna None
            finish_reason = getattr(response, 'finish_reason', 'N/A')
            prompt_feedback = getattr(response, 'prompt_feedback', 'N/A')
            emoji_logger.model_warning(
                "Gemini response has no valid part, indicating a potential issue (e.g., safety filters). Triggering fallback.",
                finish_reason=finish_reason,
                prompt_feedback=str(prompt_feedback),
                error=str(e)
            )
            return None


class OpenAI:
    """Wrapper REAL para OpenAI API"""
    def __init__(self, id, api_key):
        self.id = id
        self.api_key = api_key
        self.client = None

        if OPENAI_AVAILABLE and api_key:
            # Configurar OpenAI REAL
            self.client = openai.AsyncOpenAI(api_key=api_key)
        else:
            emoji_logger.system_warning(
                "OpenAI client não pôde ser inicializado. Verifique a disponibilidade da biblioteca e a OPENAI_API_KEY."
            )

    async def achat(self, messages):
        """Chamada REAL para OpenAI API com suporte para nosso formato multimodal interno."""
        if not self.client:
            emoji_logger.model_error("Tentativa de usar o fallback OpenAI, mas o cliente não está configurado.")
            return None

        # Transforma o histórico de mensagens para o formato da OpenAI
        openai_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            
            if isinstance(content, list):
                # Mensagem multimodal
                new_content_parts = []
                for part in content:
                    part_type = part.get("type")
                    if part_type == "text":
                        new_content_parts.append(part)
                    elif part_type == "media":
                        # Converte nosso tipo 'media' para 'image_url' da OpenAI
                        media_data = part.get("media_data", {})
                        mime_type = media_data.get("mime_type")
                        base64_content = media_data.get("content")
                        if mime_type and base64_content and "image" in mime_type:
                            new_content_parts.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_content}"
                                }
                            })
                        else:
                            # Ignora mídias não suportadas por enquanto para evitar erros
                            emoji_logger.model_warning(f"Mídia do tipo '{mime_type}' não suportada pelo wrapper OpenAI. Ignorando.")
                
                if new_content_parts:
                    openai_messages.append({"role": role, "content": new_content_parts})

            else:
                # Mensagem de texto simples
                openai_messages.append({"role": role, "content": content})

        try:
            params = {
                "model": self.id,
                "messages": openai_messages,
            }

            if 'o3-mini' not in self.id:
                params["temperature"] = 0.7

            response = await self.client.chat.completions.create(**params)

            return type('Response', (), {
                'content': response.choices[0].message.content
            })()

        except Exception as e:
            emoji_logger.model_error(f"Erro na API OpenAI: {e}")
            return None


class ModelManager:
    """
    Gerenciador SIMPLES de modelos AI com fallback automático
    Mantém 100% da funcionalidade de forma modular
    """

    def __init__(self):
        self.primary_model = None
        self.fallback_model = None
        self.reasoning_model = None
        self.retry_count = 0
        self.max_retries = 5
        self.is_initialized = False

    def initialize(self):
        """Inicialização SIMPLES dos modelos"""
        if self.is_initialized:
            return

        # Modelo primário - Gemini
        try:
            if settings.primary_ai_model.startswith("gemini"):
                self.primary_model = Gemini(
                    id=settings.primary_ai_model,
                    api_key=settings.google_api_key
                )
                emoji_logger.system_ready(
                    "Modelo primário Gemini configurado",
                    model=settings.primary_ai_model
                )
        except Exception as e:
            emoji_logger.system_warning(f"Erro ao configurar Gemini: {e}")

        # Modelo fallback - OpenAI
        try:
            if (settings.fallback_ai_model and
                    (settings.fallback_ai_model.startswith("gpt") or settings.fallback_ai_model.startswith("o3"))):
                self.fallback_model = OpenAI(
                    id=settings.fallback_ai_model,
                    api_key=settings.openai_api_key
                )
                emoji_logger.system_ready(
                    "Modelo fallback OpenAI configurado",
                    model=settings.fallback_ai_model
                )
        except Exception as e:
            emoji_logger.system_warning(f"Erro ao configurar OpenAI: {e}")

        # Modelo reasoning - Gemini thinking
        try:
            if settings.agno_reasoning_enabled:
                self.reasoning_model = Gemini(
                    id="gemini-2.0-flash-thinking",
                    api_key=settings.google_api_key
                )
                emoji_logger.system_ready(
                    "Modelo reasoning configurado",
                    model="gemini-2.0-flash-thinking"
                )
        except Exception as e:
            emoji_logger.system_warning(f"Erro ao configurar reasoning: {e}")

        self.is_initialized = True
        emoji_logger.system_ready(
            "Sistema de modelos configurado",
            primary_model=settings.primary_ai_model,
            fallback_available=self.fallback_model is not None,
            reasoning_enabled=self.reasoning_model is not None
        )

    async def get_response(
            self,
            messages: list,
            system_prompt: Optional[str] = None,
            use_reasoning: bool = False,
            temperature: float = 0.7,
            max_tokens: int = 2000
    ) -> Optional[str]:
        """
        Obtém resposta REAL do modelo com fallback automático
        """
        model_to_use = self.primary_model
        if use_reasoning and self.reasoning_model:
            model_to_use = self.reasoning_model

        if use_reasoning and self.reasoning_model:
            try:
                response = await self._try_model(
                    self.reasoning_model, messages, system_prompt
                )
                if response:
                    return response
            except Exception as e:
                emoji_logger.model_error(f"Erro no reasoning model: {e}")

        if self.primary_model:
            try:
                response = await self._try_model(
                    self.primary_model, messages, system_prompt
                )
                if response:
                    return response
            except Exception as e:
                emoji_logger.model_error(f"Erro no modelo primário: {e}")

        if self.fallback_model:
            emoji_logger.model_warning(f"Modelo primário falhou. Acionando fallback para {self.fallback_model.id}.")
            try:
                response = await self._try_model(
                    self.fallback_model, messages, system_prompt
                )
                if response:
                    emoji_logger.model_warning(f"Usando modelo fallback: {self.fallback_model.id}")
                    return response
            except Exception as e:
                emoji_logger.model_error(f"Erro no modelo fallback: {e}")

        emoji_logger.service_error("Todos os modelos falharam")
        return None

    async def _try_model(
            self,
            model: Any,
            messages: list,
            system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Tenta obter resposta de um modelo específico
        """
        try:
            emoji_logger.system_debug(
                "Enviando para o LLM",
                model=model.id,
                history_length=len(messages),
                system_prompt_length=len(system_prompt or "")
            )
            if isinstance(model, OpenAI) and system_prompt:
                messages_with_system = [{"role": "system", "content": system_prompt}] + messages
                response = await model.achat(messages_with_system)
            elif isinstance(model, Gemini):
                async def gemini_call():
                    return await model.achat(messages, system_prompt=system_prompt)
                response = await self.retry_with_backoff(gemini_call)
            else:
                # Fallback para outros modelos que possam ser adicionados
                response = await model.achat(messages)

            if response and response.content:
                emoji_logger.system_debug(
                    "Resposta recebida do LLM",
                    model=model.id,
                    response_length=len(response.content)
                )
                return response.content
            else:
                emoji_logger.system_warning(
                    "Resposta do LLM vazia",
                    model=model.id
                )
                return "Oi! Me da um minutinho que te respondo."

        except Exception as e:
            emoji_logger.model_error(f"Erro ao chamar modelo: {e}")
            return "Olá! Te retorno em alguns minutos!!"

    async def retry_with_backoff(
            self,
            func,
            max_attempts: int = 3,
            initial_delay: float = 1.0
    ):
        """
        Retry com backoff exponencial SIMPLES
        """
        delay = initial_delay

        for attempt in range(max_attempts):
            try:
                result = await func()
                if result:
                    return result
            except ResourceExhausted as e:
                if attempt < max_attempts - 1:
                    emoji_logger.model_warning(
                        f"Erro de quota (429). Tentativa {attempt + 1} falhou, "
                        f"aguardando {delay}s. Detalhes: {e}"
                    )
                    await asyncio.sleep(delay)
                    delay *= 2
                else:
                    emoji_logger.model_error(
                        f"Todas as tentativas falharam após erro de quota: {e}"
                    )
                    raise e
            except Exception as e:
                emoji_logger.model_error(
                    f"Erro não relacionado a quota. Todas as tentativas falharam: {e}"
                )
                raise e
        return None

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre os modelos configurados"""
        return {
            "primary": (
                settings.primary_ai_model if self.primary_model else None
            ),
            "fallback": (
                settings.fallback_ai_model if self.fallback_model else None
            ),
            "reasoning": (
                "gemini-2.0-flash-thinking" if self.reasoning_model else None
            ),
            "initialized": self.is_initialized
        }
"""
Audio Service - Serviço para envio de áudio via Evolution API
Implementa o envio do áudio inicial do presidente/técnico Hélio dos Anjos
"""

import base64
import aiohttp
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.logger import emoji_logger


class AudioService:
    """Serviço para gerenciar envio de áudios via Evolution API"""

    def __init__(self):
        self.evolution_url = (
            settings.evolution_api_url or settings.evolution_base_url
        )
        self.api_key = settings.evolution_api_key
        self.instance_name = (
            settings.evolution_instance_name or "SDR IA Náutico"
        )
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        # URL do áudio inicial do presidente Hélio dos Anjos
        self.initial_audio_url = (
            "https://qvehtvvlalskxbeaflzs.supabase.co/storage/v1/object/public/"
            "documents/AUDIO-ENVIAR-NO-INICIO-DA-CONVERSA-2%20(1).mp3"
        )
        
        self._session_timeout = aiohttp.ClientTimeout(total=60)

    async def _get_session(self):
        """Cria sessão HTTP com configurações apropriadas"""
        connector = aiohttp.TCPConnector(
            limit=10, limit_per_host=5, ttl_dns_cache=300
        )
        return aiohttp.ClientSession(
            connector=connector, timeout=self._session_timeout
        )

    async def _download_and_convert_audio(self, audio_url: str) -> str:
        """
        Baixa o áudio da URL e converte para Base64
        """
        try:
            emoji_logger.service_info(f"📥 Baixando áudio de: {audio_url}")
            
            async with await self._get_session() as session:
                async with session.get(audio_url) as response:
                    if response.status == 200:
                        audio_content = await response.read()
                        
                        # Converter para Base64
                        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                        
                        emoji_logger.service_success(
                            f"✅ Áudio convertido para Base64. Tamanho: {len(audio_base64)} chars"
                        )
                        return audio_base64
                    else:
                        raise Exception(f"Erro HTTP {response.status} ao baixar áudio")
                        
        except Exception as e:
            emoji_logger.service_error(f"Erro ao baixar/converter áudio: {e}")
            raise

    async def send_initial_audio(
        self, 
        phone_number: str,
        lead_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Envia o áudio inicial do presidente Hélio dos Anjos via Evolution API
        """
        try:
            if settings.environment == "development" or settings.debug:
                emoji_logger.service_info(
                    "🔧 Modo desenvolvimento - Simulando envio de áudio"
                )
                return {
                    "success": True,
                    "message": "Áudio simulado em desenvolvimento",
                    "simulated": True
                }
            
            # Limpar e formatar número de telefone
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            whatsapp_number = f"{clean_phone}@s.whatsapp.net"
            
            emoji_logger.service_info(
                f"🎵 Enviando áudio inicial para {clean_phone}"
            )
            
            # Baixar e converter áudio para Base64
            audio_base64 = await self._download_and_convert_audio(self.initial_audio_url)
            
            # Preparar payload para Evolution API
            payload = {
                "number": whatsapp_number,
                "audio": audio_base64,
                "delay": 1000,
                "presence": "recording"
            }
            
            # Enviar via Evolution API
            async with await self._get_session() as session:
                url = f"{self.evolution_url}/message/sendWhatsAppAudio/{self.instance_name}"
                
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        
                        emoji_logger.service_success(
                            f"✅ Áudio inicial enviado com sucesso para {clean_phone}"
                        )
                        
                        return {
                            "success": True,
                            "message": "Áudio inicial enviado com sucesso",
                            "phone_number": clean_phone,
                            "message_id": result.get("key", {}).get("id"),
                            "audio_url": self.initial_audio_url
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"Erro {response.status}: {error_text}")
                        
        except Exception as e:
            emoji_logger.service_error(f"Erro ao enviar áudio inicial: {e}")
            return {
                "success": False,
                "message": f"Erro ao enviar áudio: {str(e)}",
                "phone_number": phone_number
            }

    async def send_custom_audio(
        self,
        phone_number: str,
        audio_url: str,
        lead_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Envia áudio customizado via Evolution API
        """
        try:
            if settings.environment == "development" or settings.debug:
                emoji_logger.service_info(
                    "🔧 Modo desenvolvimento - Simulando envio de áudio customizado"
                )
                return {
                    "success": True,
                    "message": "Áudio customizado simulado em desenvolvimento",
                    "simulated": True
                }
            
            # Limpar e formatar número de telefone
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            whatsapp_number = f"{clean_phone}@s.whatsapp.net"
            
            emoji_logger.service_info(
                f"🎵 Enviando áudio customizado para {clean_phone}"
            )
            
            # Baixar e converter áudio para Base64
            audio_base64 = await self._download_and_convert_audio(audio_url)
            
            # Preparar payload para Evolution API
            payload = {
                "number": whatsapp_number,
                "audio": audio_base64,
                "delay": 1000,
                "presence": "recording"
            }
            
            # Enviar via Evolution API
            async with await self._get_session() as session:
                url = f"{self.evolution_url}/message/sendWhatsAppAudio/{self.instance_name}"
                
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        
                        emoji_logger.service_success(
                            f"✅ Áudio customizado enviado com sucesso para {clean_phone}"
                        )
                        
                        return {
                            "success": True,
                            "message": "Áudio customizado enviado com sucesso",
                            "phone_number": clean_phone,
                            "message_id": result.get("key", {}).get("id"),
                            "audio_url": audio_url
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"Erro {response.status}: {error_text}")
                        
        except Exception as e:
            emoji_logger.service_error(f"Erro ao enviar áudio customizado: {e}")
            return {
                "success": False,
                "message": f"Erro ao enviar áudio: {str(e)}",
                "phone_number": phone_number
            }

    async def validate_audio_url(self, audio_url: str) -> Dict[str, Any]:
        """
        Valida se uma URL de áudio está acessível
        """
        try:
            async with await self._get_session() as session:
                async with session.head(audio_url) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        content_length = response.headers.get('content-length', '0')
                        
                        return {
                            "success": True,
                            "accessible": True,
                            "content_type": content_type,
                            "size": int(content_length) if content_length.isdigit() else 0,
                            "message": "Áudio acessível"
                        }
                    else:
                        return {
                            "success": False,
                            "accessible": False,
                            "message": f"Erro HTTP {response.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "accessible": False,
                "message": f"Erro ao validar URL: {str(e)}"
            }
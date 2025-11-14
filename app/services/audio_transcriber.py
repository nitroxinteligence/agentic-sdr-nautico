"""
Audio Transcription Service - Transcreve áudios do WhatsApp
Engine único: OpenAI Whisper-1
"""
from pydub import AudioSegment
import io
import base64
from typing import Dict, Any
from loguru import logger
from app.utils.logger import emoji_logger
import tempfile
import os
import subprocess
from app.config import settings


def validate_audio_base64(audio_data: str) -> tuple[bool, str]:
    """
    Valida se o áudio está em formato base64 válido
    """
    if not audio_data:
        return False, "empty"
    if audio_data.startswith("data:"):
        if ";base64," in audio_data:
            audio_data = audio_data.split(";base64,")[1]
            return True, "data_url_extracted"
        return False, "invalid_data_url"
    if audio_data.startswith(("http://", "https://")):
        return False, "url_not_base64"
    try:
        if len(audio_data) > 50:
            base64.b64decode(
                audio_data[:100] if len(audio_data) >= 100 else audio_data
            )
            return True, "base64"
        else:
            return False, "too_short"
    except Exception:
        return False, "invalid_base64"


class AudioTranscriber:
    """
    Serviço de transcrição de áudio usando SpeechRecognition.
    """

    def __init__(self):
        """Inicializa o transcriber com Google e OpenAI como fallback"""
        self.openai_available = False
        try:
            if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                self.openai_available = True
                emoji_logger.system_info(
                    "✅ AudioTranscriber com Whisper-1 (OpenAI)"
                )
            else:
                emoji_logger.system_info(
                    "❌ OPENAI_API_KEY ausente - Whisper indisponível"
                )
        except Exception as e:
            logger.warning(f"⚠️ OpenAI não disponível para fallback: {e}")
            emoji_logger.system_info(
                "❌ Whisper indisponível"
            )

    async def transcribe_from_base64(
        self,
        audio_base64: str,
        mimetype: str = "audio/ogg",
        language: str = "pt-BR"
    ) -> Dict[str, Any]:
        """
        Transcreve áudio de base64 para texto
        """
        if not audio_base64:
            return {"text": "", "status": "error", "error": "Áudio vazio"}
        try:
            emoji_logger.system_info(
                f"Iniciando transcrição de áudio ({mimetype}) via Whisper-1"
            )
            is_valid, format_type = validate_audio_base64(audio_base64)
            if not is_valid:
                logger.error(f"Formato de áudio inválido: {format_type}")
                return {
                    "text": "", "status": "error",
                    "error": f"Formato inválido: {format_type}"
                }
            if format_type == "data_url_extracted":
                audio_base64 = audio_base64.split(";base64,")[1]
            try:
                audio_bytes = base64.b64decode(audio_base64)
            except Exception as e:
                logger.error(f"Erro ao decodificar base64: {e}")
                return {
                    "text": "", "status": "error",
                    "error": f"Erro ao decodificar: {e}"
                }
            # Converter com ffmpeg para WAV 16k mono e transcrever com Whisper
            try:
                if not self.openai_available:
                    return {
                        "text": "", "status": "error",
                        "error": "OPENAI_API_KEY ausente"
                    }
                # Escrever bytes em arquivo temporário
                audio_format = (mimetype.split("/")[1] if "/" in mimetype else "ogg")
                with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_in:
                    temp_in.write(audio_bytes)
                    temp_in_path = temp_in.name
                # Converter para WAV
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_out:
                    temp_out_path = temp_out.name
                cmd = [
                    'ffmpeg', '-i', temp_in_path, '-acodec', 'pcm_s16le',
                    '-ar', '16000', '-ac', '1', '-f', 'wav', '-loglevel', 'error', '-y', temp_out_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0 or not os.path.exists(temp_out_path) or os.path.getsize(temp_out_path) == 0:
                    raise Exception(f"ffmpeg falhou: {result.stderr}")
                # Duração
                audio_seg = AudioSegment.from_wav(temp_out_path)
                duration_seconds = len(audio_seg) / 1000.0
                # Whisper
                with open(temp_out_path, 'rb') as audio_file:
                    transcription = self.openai_client.audio.transcriptions.create(
                        model='whisper-1', file=audio_file, language='pt'
                    )
                text = getattr(transcription, 'text', '') or ''
                return {
                    "text": text, "status": "success",
                    "duration": duration_seconds,
                    "language": language, "engine": "whisper-1"
                }
            except Exception as e:
                logger.error(f"Erro Whisper: {e}")
                return {
                    "text": "", "status": "error",
                    "error": f"Erro ao transcrever: {e}"
                }
            finally:
                try:
                    if 'temp_in_path' in locals() and os.path.exists(temp_in_path):
                        os.unlink(temp_in_path)
                except Exception:
                    pass
                try:
                    if 'temp_out_path' in locals() and os.path.exists(temp_out_path):
                        os.unlink(temp_out_path)
                except Exception:
                    pass
        except Exception as e:
            logger.exception(f"Erro crítico no AudioTranscriber: {e}")
            return {
                "text": "", "status": "error", "error": f"Erro crítico: {e}"
            }

    async def transcribe_from_file(
        self, file_path: str, language: str = "pt-BR"
    ) -> Dict[str, Any]:
        """
        Transcreve áudio de um arquivo
        """
        try:
            with open(file_path, 'rb') as f:
                audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            extension = os.path.splitext(file_path)[1].lower()
            mimetype_map = {
                '.ogg': 'audio/ogg', '.mp3': 'audio/mp3',
                '.wav': 'audio/wav', '.m4a': 'audio/m4a',
                '.opus': 'audio/opus'
            }
            mimetype = mimetype_map.get(extension, 'audio/ogg')
            return await self.transcribe_from_base64(
                audio_base64, mimetype, language
            )
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            return {
                "text": "", "status": "error",
                "error": f"Erro ao ler arquivo: {e}"
            }


audio_transcriber = AudioTranscriber()

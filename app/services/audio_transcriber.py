"""
Audio Transcription Service - Transcreve áudios do WhatsApp
Prioridade: 1º Google Speech (gratuito), 2º OpenAI Whisper-1 (barato: $0.006/min)
"""
import speech_recognition as sr
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
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.openai_available = False
        try:
            if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                self.openai_available = True
                emoji_logger.system_info(
                    "✅ AudioTranscriber com Google e Whisper"
                )
            else:
                emoji_logger.system_info(
                    "AudioTranscriber usando apenas Google Speech"
                )
        except Exception as e:
            logger.warning(f"⚠️ OpenAI não disponível para fallback: {e}")
            emoji_logger.system_info(
                "AudioTranscriber usando apenas Google Speech"
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
                f"Iniciando transcrição de áudio ({mimetype})"
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
            try:
                audio_format = (
                    mimetype.split("/")[1] if "/" in mimetype else "ogg"
                )
                is_encrypted = False
                if len(audio_bytes) > 4:
                    magic = audio_bytes[:4]
                    known_formats = [
                        b'OggS', b'RIFF', b'\xff\xfb', b'\xff\xf3',
                        b'\xff\xf2', b'ftyp', b'ID3'
                    ]
                    is_encrypted = not any(
                        magic.startswith(fmt) for fmt in known_formats
                    )
                    if is_encrypted:
                        audio_format = "opus"
                with tempfile.NamedTemporaryFile(
                    suffix=f".{audio_format}", delete=False
                ) as temp_audio:
                    temp_audio.write(audio_bytes)
                    temp_audio_path = temp_audio.name
                audio = None
                if ("opus" in mimetype.lower() or
                        audio_format == "ogg" or is_encrypted):
                    try:
                        with tempfile.NamedTemporaryFile(
                            suffix=".wav", delete=False
                        ) as temp_wav:
                            temp_wav_path = temp_wav.name
                        cmd = [
                            'ffmpeg', '-i', temp_audio_path, '-acodec',
                            'pcm_s16le', '-ar', '16000', '-ac', '1', '-f',
                            'wav', '-loglevel', 'error', '-y', temp_wav_path
                        ]
                        result = subprocess.run(
                            cmd, capture_output=True, text=True, timeout=30
                        )
                        if result.returncode == 0:
                            if (os.path.exists(temp_wav_path) and
                                    os.path.getsize(temp_wav_path) > 0):
                                audio = AudioSegment.from_wav(temp_wav_path)
                            else:
                                raise Exception("ffmpeg criou arquivo vazio")
                            os.unlink(temp_wav_path)
                        else:
                            raise Exception(f"ffmpeg falhou: {result.stderr}")
                    except Exception as e:
                        logger.error(f"Erro ao converter com ffmpeg: {e}")
                if audio is None:
                    formats_to_try = [
                        audio_format, "ogg", "mp3", "m4a", "wav"
                    ]
                    for fmt in formats_to_try:
                        try:
                            if fmt == "ogg":
                                audio = AudioSegment.from_ogg(temp_audio_path)
                            else:
                                audio = AudioSegment.from_file(
                                    temp_audio_path, format=fmt
                                )
                            break
                        except Exception:
                            continue
                if audio is None:
                    raise Exception("Não foi possível carregar o áudio")
                wav_io = io.BytesIO()
                audio.export(wav_io, format="wav")
                wav_io.seek(0)
                duration_seconds = len(audio) / 1000.0
            except Exception as e:
                logger.error(f"Erro ao converter áudio: {e}")
                return {
                    "text": "", "status": "error",
                    "error": f"Erro ao processar: {e}"
                }
            finally:
                if 'temp_audio_path' in locals():
                    os.unlink(temp_audio_path)
            wav_path_for_fallback = None
            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as temp_wav_fallback:
                    wav_path_for_fallback = temp_wav_fallback.name
                    wav_io.seek(0)
                    temp_wav_fallback.write(wav_io.read())
                with sr.AudioFile(wav_io) as source:
                    self.recognizer.adjust_for_ambient_noise(
                        source, duration=0.5
                    )
                    audio_data = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(
                            audio_data, language=language, show_all=False
                        )
                        return {
                            "text": text, "status": "success",
                            "duration": duration_seconds,
                            "language": language, "engine": "google"
                        }
                    except sr.UnknownValueError:
                        if self.openai_available and wav_path_for_fallback:
                            try:
                                with open(
                                    wav_path_for_fallback, "rb"
                                ) as audio_file:
                                    transcription = (
                                        self.openai_client.audio.transcriptions.create(
                                            model="whisper-1",
                                            file=audio_file,
                                            language="pt"
                                        )
                                    )
                                text = transcription.text
                                return {
                                    "text": text, "status": "success",
                                    "duration": duration_seconds,
                                    "language": language,
                                    "engine": "whisper-1",
                                    "note": "Transcrito com OpenAI Whisper"
                                }
                            except Exception as whisper_error:
                                logger.error(f"Whisper falhou: {whisper_error}")
                        return {
                            "text": "[Áudio não compreendido]",
                            "status": "unclear",
                            "duration": duration_seconds,
                            "language": language
                        }
                    except sr.RequestError as e:
                        logger.error(f"Erro Google Speech: {e}")
                        if self.openai_available and wav_path_for_fallback:
                            try:
                                with open(
                                    wav_path_for_fallback, "rb"
                                ) as audio_file:
                                    transcription = (
                                        self.openai_client.audio.transcriptions.create(
                                            model="whisper-1",
                                            file=audio_file,
                                            language="pt"
                                        )
                                    )
                                text = transcription.text
                                return {
                                    "text": text, "status": "success",
                                    "duration": duration_seconds,
                                    "language": language,
                                    "engine": "whisper-1-fallback",
                                    "note": "Google falhou, usado Whisper"
                                }
                            except Exception as whisper_error:
                                logger.error(
                                    f"Whisper falhou: {whisper_error}"
                                )
                        return {
                            "text": "", "status": "error",
                            "error": "Serviços de transcrição indisponíveis",
                            "duration": duration_seconds
                        }
            except Exception as e:
                logger.error(f"Erro na transcrição: {e}")
                return {
                    "text": "", "status": "error",
                    "error": f"Erro ao transcrever: {e}"
                }
            finally:
                if (wav_path_for_fallback and
                        os.path.exists(wav_path_for_fallback)):
                    os.unlink(wav_path_for_fallback)
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

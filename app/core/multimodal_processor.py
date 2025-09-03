"""
Multimodal Processor - Processamento SIMPLES de mídia
ZERO complexidade, funcionalidade total
"""

from typing import Dict, Any, List, Optional
import base64
import io
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
import PyPDF2
from docx import Document
from app.utils.logger import emoji_logger
from app.config import settings
from app.utils.dependency_checker import check_multimodal_dependencies

try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    emoji_logger.system_warning(
        "pdf2image não instalado - OCR para PDFs desabilitado"
    )


class MultimodalProcessor:
    """
    Processador SIMPLES de mídia (imagens, áudio, documentos)
    """

    def __init__(self):
        self.enabled = settings.enable_multimodal_analysis
        self.is_initialized = False
        self.dependencies = {"ocr": False, "audio": False, "pdf": False}

    def initialize(self):
        """Inicialização simples"""
        if self.is_initialized:
            return

        if self.enabled:
            self.dependencies = check_multimodal_dependencies()
            emoji_logger.system_ready("🎨 MultimodalProcessor habilitado", dependencies=self.dependencies)
        else:
            emoji_logger.system_warning("🎨 MultimodalProcessor desabilitado")

        self.is_initialized = True

    async def process_media(
            self,
            media_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processa mídia de forma SIMPLES e DIRETA
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "Processamento multimodal desabilitado"
            }

        media_type = media_data.get("type", "").lower()
        content = media_data.get("content") or media_data.get("data", "")

        try:
            if media_type == "image":
                if not self.dependencies.get("ocr"):
                    return {"success": False, "message": "Desculpe, não consigo processar imagens no momento."}
                return await self.process_image(content)
            elif media_type in ["audio", "voice"]:
                if not self.dependencies.get("audio"):
                    return {"success": False, "message": "Desculpe, não consigo processar áudios no momento."}
                return await self.process_audio(content)
            elif media_type == "document":
                # O processamento de PDF depende tanto do poppler quanto do tesseract
                if not self.dependencies.get("pdf") or not self.dependencies.get("ocr"):
                     return {"success": False, "message": "Desculpe, não consigo processar documentos no momento."}
                return await self.process_document(content)
            else:
                return {
                    "success": False,
                    "message": f"Tipo de mídia não suportado: {media_type}"
                }
        except Exception as e:
            emoji_logger.service_error(f"Erro ao processar mídia: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar mídia: {str(e)}"
            }

    async def process_image(self, image_data: str) -> Dict[str, Any]:
        """
        Processa imagem com OCR
        """
        try:
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]

            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            text = ""
            enable_ocr = getattr(settings, 'enable_ocr', True)
            if enable_ocr:
                try:
                    text = pytesseract.image_to_string(image, lang='por')
                    emoji_logger.multimodal_event(
                        f"📸 OCR extraiu {len(text)} caracteres"
                    )
                except Exception as ocr_error:
                    emoji_logger.system_warning(f"OCR falhou: {ocr_error}")

            width, height = image.size
            format_img = image.format or "unknown"

            result = {
                "success": True,
                "type": "image",
                "text": text.strip() if text else "",
                "metadata": {
                    "width": width,
                    "height": height,
                    "format": format_img
                },
                "analysis": self._analyze_image_content(text)
            }

            emoji_logger.multimodal_event(
                f"✅ Imagem processada: {width}x{height}"
            )
            return result

        except Exception as e:
            emoji_logger.service_error(f"Erro ao processar imagem: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar imagem: {str(e)}"
            }

    async def process_audio(self, audio_data: str) -> Dict[str, Any]:
        """
        Processa áudio com transcrição
        """
        # Verificar se a transcrição de voz está habilitada
        if not getattr(settings, 'enable_voice_message_transcription', True):
            return {
                "success": False,
                "message": "Transcrição de mensagens de voz está desabilitada"
            }
            
        try:
            if "base64," in audio_data:
                audio_data = audio_data.split("base64,")[1]

            audio_bytes = base64.b64decode(audio_data)
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_buffer) as source:
                audio_record = recognizer.record(source)
                text = recognizer.recognize_google(
                    audio_record, language="pt-BR"
                )

            result = {
                "success": True,
                "type": "audio",
                "text": text,
                "metadata": {
                    "duration": len(audio) / 1000.0,
                    "channels": audio.channels,
                    "sample_rate": audio.frame_rate
                }
            }

            emoji_logger.multimodal_event(
                f"🎤 Áudio transcrito: {len(text)} caracteres"
            )
            return result

        except Exception as e:
            emoji_logger.service_error(f"Erro ao processar áudio: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar áudio: {str(e)}"
            }

    async def process_document(self, doc_data: str) -> Dict[str, Any]:
        """
        Processa documento (PDF, DOCX) com OCR inteligente para PDFs
        """
        try:
            if "base64," in doc_data:
                doc_data = doc_data.split("base64,")[1]

            doc_bytes = base64.b64decode(doc_data)
            doc_buffer = io.BytesIO(doc_bytes)

            text = ""
            doc_type = "unknown"
            ocr_used = False

            try:
                pdf_reader = PyPDF2.PdfReader(doc_buffer)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                doc_type = "pdf"

                if (not text or len(
                        text.strip()) < 10) and PDF2IMAGE_AVAILABLE:
                    emoji_logger.multimodal_event(
                        "📸 PDF sem texto detectado, aplicando OCR..."
                    )
                    doc_buffer.seek(0)
                    images = convert_from_bytes(doc_buffer.read())
                    ocr_texts = []
                    for i, image in enumerate(images):
                        try:
                            page_text = pytesseract.image_to_string(
                                image, lang='por'
                            )
                            if page_text.strip():
                                ocr_texts.append(page_text)
                                emoji_logger.multimodal_event(
                                    f"📄 OCR página {i+1}: "
                                    f"{len(page_text)} caracteres"
                                )
                        except Exception as ocr_error:
                            emoji_logger.system_warning(
                                f"OCR falhou na página {i+1}: {ocr_error}"
                            )
                    if ocr_texts:
                        text = "\n\n".join(ocr_texts)
                        ocr_used = True
                        emoji_logger.multimodal_event(
                            f"✅ OCR completo: {len(text)} caracteres extraídos"
                        )
            except Exception:
                try:
                    doc_buffer.seek(0)
                    doc = Document(doc_buffer)
                    text = "\n".join([p.text for p in doc.paragraphs])
                    doc_type = "docx"
                except Exception:
                    pass

            if text:
                analysis = self._analyze_document_content(text)
                result = {
                    "success": True,
                    "type": "document",
                    "text": text,
                    "metadata": {
                        "doc_type": doc_type,
                        "char_count": len(text),
                        "ocr_used": ocr_used
                    },
                    "analysis": analysis
                }
                if analysis.get("bill_value"):
                    emoji_logger.multimodal_event(
                        f"💰 Valor detectado: R$ {analysis['bill_value']:.2f}"
                    )
                emoji_logger.multimodal_event(
                    f"📄 Documento processado: {doc_type} "
                    f"({'via OCR' if ocr_used else ''})"
                )
                return result
            else:
                return {
                    "success": False,
                    "message": "Não foi possível extrair texto do documento"
                }
        except Exception as e:
            emoji_logger.system_error(f"Erro ao processar documento: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar documento: {str(e)}"
            }

    def _analyze_document_content(self, text: str) -> Dict[str, Any]:
        """
        Análise inteligente do conteúdo do documento
        """
        analysis = {
            "has_text": bool(text and text.strip()),
            "is_bill": False,
            "bill_value": None,
            "document_type": None
        }
        if text:
            text_lower = text.lower()
            if any(word in text_lower for word in [
                "boleto", "cobrança", "vencimento"
            ]):
                analysis["document_type"] = "boleto"
                analysis["is_bill"] = True
            elif any(word in text_lower for word in [
                "mensalidade", "náutico", "sócio", "contribuição"
            ]):
                analysis["document_type"] = "mensalidade_nautico"
                analysis["is_bill"] = True

            if analysis["is_bill"]:
                analysis["bill_value"] = self._extract_bill_value_from_text(text)
        return analysis

    def _analyze_image_content(self, text: str) -> Dict[str, Any]:
        """
        Análise do conteúdo da imagem, incluindo validação para comprovantes de pagamento do Náutico.
        """
        analysis = {
            "has_text": bool(text and text.strip()),
            "is_bill": False,
            "is_payment_receipt": False,
            "bill_value": None,
            "payment_value": None,
            "is_valid_nautico_payment": False,
            "payer_name": None
        }
        
        if text:
            text_lower = text.lower()
            
            # Detectar se é mensalidade do Náutico
            bill_keywords = ["mensalidade", "náutico", "sócio", "contribuição", "clube"]
            if any(keyword in text_lower for keyword in bill_keywords):
                analysis["is_bill"] = True
                analysis["bill_value"] = self._extract_bill_value_from_text(text)
            
            # Detectar se é comprovante de pagamento
            payment_keywords = ["comprovante", "pix", "transferência", "pagamento", "débito", "crédito", "transação"]
            if any(keyword in text_lower for keyword in payment_keywords):
                analysis["is_payment_receipt"] = True
                analysis["payment_value"] = self._extract_payment_value_from_text(text)
                analysis["payer_name"] = self._extract_payer_name_from_text(text)
                
                # Validar se é um valor válido do programa de sócios do Náutico
                if analysis["payment_value"]:
                    analysis["is_valid_nautico_payment"] = self._is_valid_nautico_payment_value(analysis["payment_value"])
        
        return analysis

    def _extract_bill_value_from_text(self, text: str) -> Optional[float]:
        """
        Lógica de extração de valor de conta robusta e centralizada.
        """
        import re
        from collections import Counter

        patterns = [
            r"R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"R\$\s*(\d+,\d{2})",
            r"(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"(\d+,\d{2})"
        ]
        all_values = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    value_str = match.replace(".", "").replace(",", ".")
                    value = float(value_str)
                    if 10 <= value <= 100000:
                        all_values.append(value)
                except Exception:
                    pass
        
        if not all_values:
            return None

        # Lógica de seleção do valor mais provável
        selected_value = None
        text_lower = text.lower()
        total_patterns = [
            r"total\s*a?\s*pagar[:\s]*R?$\\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"valor\s*total[:\s]*R?$\\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"total[:\s]*R?$\\s*(\d{1,3}(?:\.\d{3})*,\d{2})"
        ]
        for pattern in total_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    value_str = matches[0].replace(".", "").replace(",", ".")
                    selected_value = float(value_str)
                    break
                except Exception:
                    pass
        
        if selected_value is None:
            rounded_values = [round(v, 2) for v in all_values]
            value_counts = Counter(rounded_values)
            most_common = value_counts.most_common(1)
            if most_common and most_common[0][1] >= 2: # Se um valor aparece 2+ vezes
                selected_value = most_common[0][0]

        if selected_value is None:
            selected_value = max(all_values) # Fallback para o maior valor encontrado

        emoji_logger.multimodal_event(
            f"💵 Valores encontrados: {sorted(set([round(v, 2) for v in all_values]))[:10]},"
            f" selecionado: R$ {selected_value:.2f}"
        )
        return selected_value

    def _extract_payment_value_from_text(self, text: str) -> Optional[float]:
        """
        Extração de valor de comprovante de pagamento.
        """
        import re
        
        # Buscar por padrões específicos de valores em comprovantes
        payment_patterns = [
            r"valor\s*(?:da\s*)?(?:transação|transferência|pagamento)[:\s]*R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"(\d{1,3}(?:\.\d{3})*,\d{2})",
        ]
        
        all_values = []
        for pattern in payment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value_str = match.replace(".", "").replace(",", ".")
                    value = float(value_str)
                    if 1 <= value <= 50000:  # Range amplo para valores de pagamento
                        all_values.append(value)
                except Exception:
                    pass
        
        if all_values:
            # Retornar o primeiro valor encontrado (geralmente é o valor principal)
            return all_values[0]
        
        return None

    def _extract_payer_name_from_text(self, text: str) -> Optional[str]:
        """
        Extração de nome do pagador do comprovante.
        """
        import re
        
        # Padrões para encontrar nomes em comprovantes
        name_patterns = [
            r"(?:pagador|remetente|de)[:\s]*([A-ZÁÊÇÕ][a-záêçõ\s]+[A-ZÁÊÇÕ])",
            r"origem[:\s]*([A-ZÁÊÇÕ][a-záêçõ\s]+)",
            r"nome[:\s]*([A-ZÁÊÇÕ][a-záêçõ\s]+)",
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                name = matches[0].strip()
                # Validar se parece um nome (pelo menos 2 palavras)
                if len(name.split()) >= 2 and len(name) <= 50:
                    return name
        
        return None

    def _is_valid_nautico_payment_value(self, value: float) -> bool:
        """
        Valida se o valor está na lista de valores válidos do programa de sócios do Náutico.
        """
        valid_values = [399.90, 99.90, 39.90, 24.90, 79.90, 3000.00, 1518.00, 12.90, 11.00, 50.00, 10.00]
        
        # Considerar uma pequena margem de erro para valores decimais
        tolerance = 0.01
        for valid_value in valid_values:
            if abs(value - valid_value) <= tolerance:
                return True
        
        return False

    def get_supported_types(self) -> List[str]:
        """Retorna tipos de mídia suportados"""
        return ["image", "audio", "voice", "document", "pdf", "docx"]

    def is_enabled(self) -> bool:
        """Verifica se o processamento multimodal está habilitado"""
        return self.enabled
"""
Dependency Checker - Verifica a presença de binários externos essenciais.
"""
import shutil
from app.utils.logger import emoji_logger

def check_command(command: str) -> bool:
    """Verifica se um comando existe no PATH do sistema."""
    return shutil.which(command) is not None

def check_multimodal_dependencies() -> dict:
    """
    Verifica todas as dependências necessárias para o MultimodalProcessor
    e retorna um dicionário com o status de cada uma.
    """
    dependencies = {
        "ocr": check_command("tesseract"),
        "audio": check_command("ffmpeg"),
        "pdf": check_command("pdftoppm"),
    }

    if not dependencies["ocr"]:
        emoji_logger.system_warning(
            "Dependência 'tesseract' não encontrada. O processamento de OCR de imagens será desativado."
        )
    if not dependencies["audio"]:
        emoji_logger.system_warning(
            "Dependência 'ffmpeg' não encontrada. O processamento de áudio será desativado."
        )
    if not dependencies["pdf"]:
        emoji_logger.system_warning(
            "Dependência 'poppler' (pdftoppm) não encontrada. O processamento de PDFs será desativado."
        )
        
    return dependencies

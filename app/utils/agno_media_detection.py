"""
AGNO Framework - Media Detection Utility
Detecção robusta de tipos de mídia com fallbacks inteligentes
Baseado nos padrões oficiais do AGNO Framework
"""

from typing import Dict, Any


class AGNOMediaDetector:
    """
    Detector de mídia baseado nos padrões AGNO Framework
    """

    def __init__(self):
        """Initialize AGNO media patterns"""
        self.image_patterns = {
            b'\xff\xd8\xff': {
                'format': 'jpeg', 'agno_class': 'Image', 'confidence': 'high'
            },
            b'\x89PNG\r\n\x1a\n': {
                'format': 'png', 'agno_class': 'Image', 'confidence': 'high'
            },
            b'GIF87a': {
                'format': 'gif', 'agno_class': 'Image', 'confidence': 'high'
            },
            b'GIF89a': {
                'format': 'gif', 'agno_class': 'Image', 'confidence': 'high'
            },
            b'RIFF': {
                'format': 'webp', 'agno_class': 'Image',
                'confidence': 'medium', 'extra_check': 'webp'
            },
            b'BM': {
                'format': 'bmp', 'agno_class': 'Image', 'confidence': 'high'
            },
            b'ftyp': {
                'format': 'heic', 'agno_class': 'Image',
                'confidence': 'medium', 'extra_check': 'heic'
            },
            b'II*\x00': {
                'format': 'tiff', 'agno_class': 'Image', 'confidence': 'high'
            },
            b'MM\x00*': {
                'format': 'tiff', 'agno_class': 'Image', 'confidence': 'high'
            },
            b'\x00\x00\x01\x00': {
                'format': 'ico', 'agno_class': 'Image', 'confidence': 'medium'
            },
            b'\xff\xee': {
                'format': 'heic_alt', 'agno_class': 'Image', 'confidence': 'low'
            }
        }
        self.document_patterns = {
            b'%PDF': {
                'format': 'pdf', 'agno_class': 'PDFReader', 'confidence': 'high'
            },
            b'PK\x03\x04': {
                'format': 'docx', 'agno_class': 'DocxReader',
                'confidence': 'medium', 'extra_check': 'zip'
            },
            b'\xd0\xcf\x11\xe0': {
                'format': 'doc', 'agno_class': 'LegacyDoc', 'confidence': 'high'
            },
        }
        self.audio_patterns = {
            b'ID3': {
                'format': 'mp3', 'agno_class': 'Audio', 'confidence': 'high'
            },
            b'\xff\xfb': {
                'format': 'mp3', 'agno_class': 'Audio', 'confidence': 'medium'
            },
            b'OggS': {
                'format': 'ogg', 'agno_class': 'Audio', 'confidence': 'high'
            },
            b'RIFF': {
                'format': 'wav', 'agno_class': 'Audio',
                'confidence': 'medium', 'extra_check': 'wav'
            },
            b'fLaC': {
                'format': 'flac', 'agno_class': 'Audio', 'confidence': 'high'
            },
        }

    def detect_media_type(self, data_bytes: bytes) -> Dict[str, Any]:
        """Detecta tipo de mídia usando padrões AGNO"""
        if not data_bytes:
            return {'detected': False, 'error': 'Dados vazios'}
        magic_bytes = data_bytes[:20] if len(data_bytes) >= 20 else data_bytes
        image_result = self._detect_image(magic_bytes, data_bytes)
        if image_result['detected']:
            return image_result
        document_result = self._detect_document(magic_bytes, data_bytes)
        if document_result['detected']:
            return document_result
        audio_result = self._detect_audio(magic_bytes, data_bytes)
        if audio_result['detected']:
            return audio_result
        return {
            'detected': False, 'format': 'unknown', 'agno_class': None,
            'confidence': 'none', 'magic_bytes': magic_bytes[:12].hex(),
            'fallback_suggestion': (
                'Use PIL/fallback ou converta para formato suportado'
            )
        }

    def _detect_image(
            self, magic_bytes: bytes, full_data: bytes
    ) -> Dict[str, Any]:
        """Detecta formato de imagem"""
        for pattern, info in self.image_patterns.items():
            if magic_bytes.startswith(pattern):
                if (
                    info.get('extra_check') and not
                    self._verify_extra_check(
                        magic_bytes, info['extra_check']
                    )
                ):
                    continue
                return {
                    'detected': True, 'media_type': 'image',
                    'format': info['format'],
                    'agno_class': info['agno_class'],
                    'confidence': info['confidence'],
                    'magic_bytes': magic_bytes[:12].hex()
                }
        return {'detected': False}

    def _detect_document(
            self, magic_bytes: bytes, full_data: bytes
    ) -> Dict[str, Any]:
        """Detecta formato de documento"""
        for pattern, info in self.document_patterns.items():
            if magic_bytes.startswith(pattern):
                return {
                    'detected': True, 'media_type': 'document',
                    'format': info['format'],
                    'agno_class': info['agno_class'],
                    'confidence': info['confidence'],
                    'magic_bytes': magic_bytes[:12].hex()
                }
        return {'detected': False}

    def _detect_audio(
            self, magic_bytes: bytes, full_data: bytes
    ) -> Dict[str, Any]:
        """Detecta formato de áudio"""
        for pattern, info in self.audio_patterns.items():
            if magic_bytes.startswith(pattern):
                if (
                    info.get('extra_check') and not
                    self._verify_extra_check(
                        magic_bytes, info['extra_check']
                    )
                ):
                    continue
                return {
                    'detected': True, 'media_type': 'audio',
                    'format': info['format'],
                    'agno_class': info['agno_class'],
                    'confidence': info['confidence'],
                    'magic_bytes': magic_bytes[:12].hex()
                }
        return {'detected': False}

    def _verify_extra_check(
            self, magic_bytes: bytes, check_type: str
    ) -> bool:
        """Verificações extras para formatos que precisam de validação"""
        if check_type == 'webp':
            return len(magic_bytes) >= 12 and magic_bytes[8:12] == b'WEBP'
        elif check_type == 'heic':
            if len(magic_bytes) >= 12:
                return magic_bytes[8:12] in (
                    b'heic', b'heix', b'hevc', b'mif1'
                )
            return False
        elif check_type == 'wav':
            return len(magic_bytes) >= 12 and magic_bytes[8:12] == b'WAVE'
        return True


tagno_media_detector = AGNOMediaDetector()

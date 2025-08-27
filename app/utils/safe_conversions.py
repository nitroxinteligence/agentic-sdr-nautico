"""
Módulo de Conversões Seguras
Fornece funções utilitárias para conversões de tipo seguras e validadas
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Converte valor para int de forma segura
    """
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value or value.lower() in ['none', 'null', 'nan']:
            return default
        value = value.replace(',', '')
        try:
            return int(float(value))
        except (ValueError, TypeError):
            logger.warning(
                f"Não foi possível converter '{value}' para int. Usando {default}"
            )
            return default
    return default


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """
    Converte valor para float de forma segura
    """
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if not value or value.lower() in ['none', 'null', 'nan']:
            return default
        value = value.replace('R, '').replace(', '').replace(',', '.')
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(
                f"Não foi possível converter '{value}' para float. Usando {default}"
            )
            return default
    return default


def safe_datetime_conversion(
    value: Any, default: Optional[datetime] = None,
    formats: Optional[list] = None
) -> Optional[datetime]:
    """
    Converte valor para datetime de forma segura
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            cleaned_value = value.replace('Z', '+00:00')
            return datetime.fromisoformat(cleaned_value)
        except (ValueError, TypeError):
            pass
        if formats:
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except (ValueError, TypeError):
                    continue
        common_formats = [
            '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M',
            '%d/%m/%Y', '%Y-%m-%d',
        ]
        for fmt in common_formats:
            try:
                return datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue
        logger.warning(f"Não foi possível converter '{value}' para datetime")
    return default


def safe_json_loads(
    value: Union[str, bytes], default: Any = None, strict: bool = False
) -> Any:
    """
    Faz parse de JSON de forma segura
    """
    if not value:
        return default
    try:
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        return json.loads(value, strict=strict)
    except json.JSONDecodeError as e:
        logger.warning(f"Erro ao fazer parse de JSON: {e}")
        return default
    except Exception as e:
        logger.error(f"Erro inesperado ao fazer parse de JSON: {e}")
        return default


def safe_json_dumps(obj: Any, default: str = "{}", **kwargs) -> str:
    """
    Serializa objeto para JSON de forma segura
    """
    try:
        kwargs.setdefault('ensure_ascii', False)
        kwargs.setdefault('default', str)
        return json.dumps(obj, **kwargs)
    except Exception as e:
        logger.warning(f"Erro ao serializar objeto para JSON: {e}")
        return default

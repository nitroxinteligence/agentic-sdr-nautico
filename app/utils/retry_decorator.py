"""Decorador de retry para operações do Supabase"""
import asyncio
import functools
from typing import Any, Callable, Optional, Tuple, Type
from loguru import logger
from app.utils.logger import emoji_logger


class SupabaseConnectionError(Exception):
    """Exceção específica para erros de conexão do Supabase"""
    pass


def supabase_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorador para retry automático em operações do Supabase
    
    Args:
        max_attempts: Número máximo de tentativas
        delay: Delay inicial entre tentativas (segundos)
        backoff_factor: Fator de multiplicação do delay a cada tentativa
        exceptions: Tupla de exceções que devem triggerar retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    result = await func(*args, **kwargs)
                    
                    # Se chegou até aqui, a operação foi bem-sucedida
                    if attempt > 1:
                        emoji_logger.service_success(
                            f"✅ Operação {func.__name__} bem-sucedida na tentativa {attempt}"
                        )
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Verifica se é um erro de conexão
                    is_connection_error = any([
                        "server disconnected" in error_msg,
                        "connection" in error_msg,
                        "timeout" in error_msg,
                        "network" in error_msg,
                        "unreachable" in error_msg,
                        "refused" in error_msg
                    ])
                    
                    if attempt == max_attempts:
                        # Última tentativa falhou
                        emoji_logger.supabase_error(
                            f"❌ Operação {func.__name__} falhou após {max_attempts} tentativas: {str(e)}",
                            table="retry_failed"
                        )
                        
                        # Se for erro de conexão, lança exceção específica
                        if is_connection_error:
                            raise SupabaseConnectionError(f"Falha de conexão após {max_attempts} tentativas: {str(e)}")
                        else:
                            raise e
                    
                    # Log da tentativa falhada
                    emoji_logger.service_warning(
                        f"⚠️ Tentativa {attempt}/{max_attempts} de {func.__name__} falhou: {str(e)}"
                    )
                    
                    # Aguarda antes da próxima tentativa
                    if attempt < max_attempts:
                        emoji_logger.service_info(
                            f"🔄 Aguardando {current_delay:.1f}s antes da próxima tentativa..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
            
            # Nunca deveria chegar aqui, mas por segurança
            raise last_exception or Exception("Erro desconhecido no retry")
        
        return wrapper
    return decorator


def supabase_safe_operation(
    default_return: Any = None,
    log_errors: bool = True
):
    """
    Decorador para operações do Supabase que devem retornar um valor padrão em caso de erro
    
    Args:
        default_return: Valor a ser retornado em caso de erro
        log_errors: Se deve logar os erros
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    emoji_logger.supabase_error(
                        f"Erro em {func.__name__}: {str(e)}",
                        table="safe_operation"
                    )
                return default_return
        
        return wrapper
    return decorator
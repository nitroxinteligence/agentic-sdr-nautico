"""
SupabaseStorage - Adapter que implementa interface do AGNO Storage usando Supabase
Elimina a necessidade de conexão direta com PostgreSQL
"""

from typing import Optional, Any
from loguru import logger
import json
import asyncio
from datetime import datetime


class SupabaseStorage:
    """
    Storage adapter que usa Supabase Client em vez de PostgreSQL direto
    """

    def __init__(
        self,
        table_name: str,
        supabase_client: Any,
        schema: str = "public",
        auto_upgrade_schema: bool = True
    ):
        self.table_name = table_name
        self.supabase_client = supabase_client
        self.session_prefix = f"{table_name}:"

    def _get_session_id(self, key: str) -> str:
        """Gera ID único para a sessão baseado na chave"""
        return f"{self.session_prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do storage"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.ensure_future(
                    self.supabase_client.get_agent_session(
                        self._get_session_id(key)
                    )
                )
                session = asyncio.run_coroutine_threadsafe(
                    future, loop
                ).result()
            else:
                session = asyncio.run(
                    self.supabase_client.get_agent_session(
                        self._get_session_id(key)
                    )
                )
            if session and 'data' in session:
                return json.loads(session['data'])
            return None
        except Exception as e:
            logger.debug(f"Erro ao buscar {key}: {e}")
            return None

    def set(self, key: str, value: Any) -> bool:
        """Define valor no storage"""
        try:
            session_data = {
                'session_id': self._get_session_id(key),
                'agent_type': self.table_name,
                'data': json.dumps(value, default=str),
                'metadata': {
                    'key': key,
                    'table_name': self.table_name,
                    'updated_at': datetime.now().isoformat()
                }
            }
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.ensure_future(
                    self.supabase_client.save_agent_session(session_data)
                )
                result = asyncio.run_coroutine_threadsafe(
                    future, loop
                ).result()
            else:
                result = asyncio.run(
                    self.supabase_client.save_agent_session(session_data)
                )
            return result is not None
        except Exception as e:
            logger.error(f"Erro ao salvar {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Remove valor do storage"""
        try:
            session_id = self._get_session_id(key)
            result = self.supabase_client.client.table(
                'agent_sessions'
            ).delete().eq('session_id', session_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.debug(f"Erro ao deletar {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        return self.get(key) is not None

    def __getattr__(self, name):
        """Proxy para métodos não implementados"""
        def dummy_method(*args, **kwargs):
            logger.debug(
                f"Método {name} chamado em SupabaseStorage - não implementado"
            )
            return None
        return dummy_method

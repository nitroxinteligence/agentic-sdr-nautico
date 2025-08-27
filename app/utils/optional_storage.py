"""
SupabaseOnlyStorage - Storage usando apenas Supabase (sem PostgreSQL)
Arquitetura ultra-simples - zero complexidade
"""

from typing import Optional, Any
from loguru import logger
from app.utils.supabase_storage import SupabaseStorage
from app.integrations.supabase_client import supabase_client


class OptionalStorage:
    """
    Storage usando apenas Supabase - SIMPLES E FUNCIONAL
    """

    def __init__(
        self,
        table_name: str,
        db_url: str = None,
        schema: str = "public",
        auto_upgrade_schema: bool = True
    ):
        self.table_name = table_name
        self.storage = SupabaseStorage(
            table_name=table_name,
            supabase_client=supabase_client,
            schema=schema,
            auto_upgrade_schema=auto_upgrade_schema
        )
        logger.info(f"✅ SupabaseStorage inicializado para: {table_name}")

    def is_connected(self) -> bool:
        """Verifica se está conectado ao storage - SEMPRE True com Supabase"""
        return True

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do storage"""
        return self.storage.get(key)

    def set(self, key: str, value: Any) -> bool:
        """Define valor no storage"""
        return self.storage.set(key, value)

    def delete(self, key: str) -> bool:
        """Remove valor do storage"""
        return self.storage.delete(key)

    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        return self.storage.exists(key)

    def __getattr__(self, name):
        """Proxy direto para SupabaseStorage - SEM FALLBACK"""
        return getattr(self.storage, name)

"""
KnowledgeService - Serviço Simples para Consultas à Base de Conhecimento
Substitui o KnowledgeAgent com implementação direta e mais simples
"""

from typing import Dict, Any, List
from datetime import datetime
from loguru import logger

from app.integrations.supabase_client import supabase_client


class KnowledgeService:
    """
    Serviço simples para consultas à base de conhecimento
    """

    def __init__(self):
        """Inicializa o serviço de conhecimento"""
        self.similarity_threshold = 0.7
        self.max_results = 5
        self._cache = {}
        self._cache_ttl = 300
        logger.info("✅ KnowledgeService inicializado (versão simplificada)")

    async def search_knowledge_base(
        self, query: str, max_results: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Busca na base de conhecimento do Supabase
        """
        try:
            cache_key = f"search_{query}_{max_results}"
            if self._is_cached(cache_key):
                logger.info(f"📋 Cache hit para query: {query[:30]}...")
                return self._cache[cache_key]['data']
            logger.info("📚 Carregando TODA a knowledge_base...")
            response = supabase_client.client.table("knowledge_base").select(
                "id, question, answer, category, keywords, created_at"
            ).limit(200).execute()
            if response.data:
                self._cache[cache_key] = {
                    'data': response.data,
                    'timestamp': datetime.now().timestamp()
                }
                logger.info(f"✅ Encontrados {len(response.data)} documentos")
                return response.data
            else:
                logger.info("ℹ️ Nenhum documento encontrado")
                return []
        except Exception as e:
            logger.error(f"❌ Erro na busca knowledge_base: {e}")
            return []

    async def search_by_category(
        self, category: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos por categoria
        """
        try:
            cache_key = f"category_{category}_{limit}"
            if self._is_cached(cache_key):
                return self._cache[cache_key]['data']
            response = supabase_client.client.table("knowledge_base").select(
                "id, question, answer, category, keywords"
            ).eq("category", category).limit(limit).execute()
            if response.data:
                self._cache[cache_key] = {
                    'data': response.data,
                    'timestamp': datetime.now().timestamp()
                }
                return response.data
            return []
        except Exception as e:
            logger.error(f"❌ Erro na busca por categoria: {e}")
            return []

    def _is_cached(self, key: str) -> bool:
        """Verifica se um item está cached e não expirou"""
        if key not in self._cache:
            return False
        cache_time = self._cache[key]['timestamp']
        if (datetime.now().timestamp() - cache_time) > self._cache_ttl:
            del self._cache[key]
            return False
        return True

    def clear_cache(self):
        """Limpa o cache"""
        self._cache.clear()
        logger.info("🧹 Cache do KnowledgeService limpo")


knowledge_service = KnowledgeService()

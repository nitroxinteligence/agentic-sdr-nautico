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
        self, query: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca RAG na base de conhecimento com similaridade textual
        """
        try:
            cache_key = f"search_{query}_{max_results}"
            if self._is_cached(cache_key):
                logger.info(f"📋 Cache hit para query: {query[:30]}...")
                return self._cache[cache_key]['data']

            logger.info(f"🔍 Buscando na knowledge_base com RAG: '{query[:50]}...'")

            # Buscar todos os documentos
            response = supabase_client.client.table("knowledge_base").select(
                "id, question, answer, category, keywords, created_at"
            ).limit(200).execute()

            if not response.data:
                logger.info("ℹ️ Nenhum documento encontrado na knowledge_base")
                return []

            # Aplicar RAG com similaridade textual simples
            scored_docs = []
            query_lower = query.lower().strip()

            for doc in response.data:
                score = self._calculate_text_similarity(query_lower, doc)
                if score > 0.1:  # Threshold mínimo
                    scored_docs.append({
                        **doc,
                        'similarity_score': score
                    })

            # Ordenar por score e limitar resultados
            scored_docs.sort(key=lambda x: x['similarity_score'], reverse=True)
            relevant_docs = scored_docs[:max_results]

            if relevant_docs:
                logger.info(f"✅ RAG encontrou {len(relevant_docs)} documentos relevantes (scores: {[round(d['similarity_score'], 2) for d in relevant_docs[:3]]})")
                self._cache[cache_key] = {
                    'data': relevant_docs,
                    'timestamp': datetime.now().timestamp()
                }
                return relevant_docs
            else:
                logger.info("ℹ️ Nenhum documento relevante encontrado pelo RAG")
                return []

        except Exception as e:
            logger.error(f"❌ Erro na busca RAG knowledge_base: {e}")
            return []

    def _calculate_text_similarity(self, query: str, doc: Dict[str, Any]) -> float:
        """
        Calcula similaridade textual simples entre query e documento
        """
        try:
            # Texto do documento para comparação
            doc_text = ""
            if doc.get("question"):
                doc_text += doc["question"].lower() + " "
            if doc.get("answer"):
                doc_text += doc["answer"].lower() + " "
            if doc.get("keywords"):
                doc_text += doc["keywords"].lower() + " "
            if doc.get("category"):
                doc_text += doc["category"].lower() + " "

            if not doc_text.strip():
                return 0.0

            # Dividir em palavras
            query_words = set(query.split())
            doc_words = set(doc_text.split())

            if not query_words or not doc_words:
                return 0.0

            # Calcular interseção (palavras em comum)
            common_words = query_words.intersection(doc_words)

            # Score baseado na proporção de palavras em comum
            if len(query_words) == 0:
                return 0.0

            similarity = len(common_words) / len(query_words)

            # Bonus para matches exatos em campos importantes
            if query in doc.get("question", "").lower():
                similarity += 0.5
            if query in doc.get("keywords", "").lower():
                similarity += 0.3
            if query in doc.get("category", "").lower():
                similarity += 0.2

            return min(similarity, 1.0)  # Máximo 1.0

        except Exception as e:
            logger.error(f"Erro no cálculo de similaridade: {e}")
            return 0.0

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

    async def add_knowledge_from_conversation(
        self, question: str, answer: str, category: str = "conversa",
        keywords: str = None, lead_info: Dict[str, Any] = None
    ) -> bool:
        """
        Adiciona novo conhecimento à base automaticamente baseado em conversas
        """
        try:
            # Validar se não é uma pergunta muito simples ou genérica
            if not self._is_valid_knowledge(question, answer):
                logger.debug(f"Conhecimento não adicionado - muito simples: {question[:50]}...")
                return False

            # Verificar se já existe conhecimento similar
            similar_docs = await self.search_knowledge_base(question, max_results=3)
            for doc in similar_docs:
                if doc.get('similarity_score', 0) > 0.8:  # Muito similar
                    logger.debug(f"Conhecimento similar já existe, não adicionando: {question[:50]}...")
                    return False

            # Gerar keywords automaticamente se não fornecidas
            if not keywords:
                keywords = self._extract_keywords(question + " " + answer)

            # Preparar dados do conhecimento
            knowledge_data = {
                "question": question.strip(),
                "answer": answer.strip(),
                "category": category,
                "keywords": keywords,
                "source": "auto_conversation",
                "auto_generated": True
            }

            # Adicionar informações do lead se disponível
            if lead_info:
                knowledge_data["source_lead_id"] = lead_info.get("id")
                knowledge_data["source_phone"] = lead_info.get("phone_number")

            # Salvar na base de conhecimento
            result = await supabase_client.add_knowledge(knowledge_data)

            if result:
                logger.info(f"📚 Novo conhecimento adicionado automaticamente: {question[:50]}...")
                self.clear_cache()  # Limpar cache para incluir novo conhecimento
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Erro ao adicionar conhecimento automático: {e}")
            return False

    def _is_valid_knowledge(self, question: str, answer: str) -> bool:
        """
        Valida se uma pergunta/resposta vale a pena ser salva como conhecimento
        """
        # Muito curtas
        if len(question.strip()) < 10 or len(answer.strip()) < 15:
            return False

        # Palavras genéricas demais
        generic_words = ['oi', 'olá', 'tchau', 'ok', 'sim', 'não', 'obrigado', 'valeu']
        question_lower = question.lower()
        if any(word in question_lower for word in generic_words):
            return False

        # Perguntas sobre agendamento (muito específicas)
        if any(word in question_lower for word in ['agendar', 'horário', 'disponível', 'quando']):
            return False

        return True

    def _extract_keywords(self, text: str) -> str:
        """
        Extrai palavras-chave automaticamente do texto
        """
        try:
            import re

            # Limpar texto
            text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
            words = text_clean.split()

            # Remover palavras muito comuns
            stop_words = {
                'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'dos', 'das',
                'em', 'no', 'na', 'nos', 'nas', 'para', 'por', 'com', 'sem', 'até',
                'que', 'é', 'são', 'foi', 'será', 'tem', 'ter', 'seu', 'sua', 'seus',
                'suas', 'me', 'te', 'se', 'lhe', 'nos', 'vos', 'lhes', 'meu', 'minha',
                'isso', 'isto', 'esse', 'essa', 'aquele', 'aquela', 'como', 'quando',
                'onde', 'porque', 'mais', 'muito', 'bem', 'já', 'ainda', 'só', 'também'
            }

            # Filtrar palavras relevantes (mais de 3 caracteres e não stop words)
            keywords = [w for w in words if len(w) > 3 and w not in stop_words]

            # Pegar as 5 primeiras palavras únicas
            unique_keywords = list(dict.fromkeys(keywords))[:5]

            return ', '.join(unique_keywords)

        except Exception as e:
            logger.error(f"Erro ao extrair keywords: {e}")
            return ""

    async def auto_learn_from_interaction(
        self, user_message: str, ai_response: str, lead_info: Dict[str, Any] = None
    ) -> bool:
        """
        Aprende automaticamente de interações interessantes
        """
        try:
            # Verificar se é uma pergunta que vale a pena salvar
            if ('?' in user_message or
                any(word in user_message.lower() for word in ['como', 'que', 'qual', 'quando', 'onde', 'porque'])):

                # Tentar adicionar como conhecimento
                success = await self.add_knowledge_from_conversation(
                    question=user_message,
                    answer=ai_response,
                    category="auto_aprendizado",
                    lead_info=lead_info
                )

                if success:
                    logger.info(f"🧠 Aprendizado automático: {user_message[:30]}...")

                return success

            return False

        except Exception as e:
            logger.error(f"❌ Erro no aprendizado automático: {e}")
            return False


knowledge_service = KnowledgeService()

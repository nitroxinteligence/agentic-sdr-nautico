"""
Response Formatter - Garante formatação correta das respostas
Processa e valida respostas do agente sem tags especiais
"""

import re
from app.utils.logger import emoji_logger


class ResponseFormatter:
    """
    Formata e valida respostas do agente
    Sistema simplificado sem tags especiais
    """

    @staticmethod
    def ensure_response_tags(response: str) -> str:
        """
        Processa resposta e remove tags desnecessárias
        Retorna texto limpo e direto
        """
        if not response:
            return "Olá! Aqui é Marina Campelo, do Náutico! Como posso te ajudar?"
        
        # CRÍTICO: Detecta se a resposta contém uma tool e NÃO a processa
        tool_pattern = r'\[\w+[:\.].*?\]'
        if re.search(tool_pattern, response):
            emoji_logger.system_debug("🔧 Tool detectada na resposta - não processando")
            return response

        # Remove todas as tags RESPOSTA_FINAL existentes
        clean_response = re.sub(r'</?RESPOSTA_FINAL>', '', response, flags=re.IGNORECASE)
        clean_response = clean_response.strip()

        # Remove padrões de "reasoning" que não devem aparecer para o usuário
        reasoning_patterns = [
            r'^(Analisando|Vou|Deixa eu|Processando|Verificando).*?\n',
            r'^(Ok|Certo|Entendi|Hmm)[\.,!]?\s*\n',
            r'^\\[.*?\\]\s*\n'
        ]
        for pattern in reasoning_patterns:
            clean_response = re.sub(
                pattern, '', clean_response,
                flags=re.MULTILINE | re.IGNORECASE
            )

        # Se ficou vazio, usar fallback
        if not clean_response or len(clean_response) < 10:
            emoji_logger.system_warning("Resposta vazia após limpeza - usando fallback")
            clean_response = "Como posso te ajudar com o programa Sócio Mais Fiel do Nordeste?"

        emoji_logger.system_success(f"✅ Resposta processada: {len(clean_response)} chars")
        return clean_response

    @staticmethod
    def validate_response_content(response: str) -> bool:
        """
        Valida se o conteúdo da resposta está adequado
        """
        if not response or len(response.strip()) < 5:
            emoji_logger.system_error("ResponseFormatter", "Resposta muito curta ou vazia")
            return False

        # Verifica se não é só números/símbolos
        if re.match(r'^[\s\d\W]+$', response.strip()):
            emoji_logger.system_error("ResponseFormatter", "Resposta sem texto válido")
            return False

        # Verifica frases proibidas (reasoning vazado)
        forbidden_phrases = [
            "vou analisar", "processando", "calculando",
            "verificando", "aguarde", "só um momento", "um minutinho"
        ]
        content_lower = response.lower()
        for phrase in forbidden_phrases:
            if phrase in content_lower:
                emoji_logger.system_warning(f"⚠️ Frase proibida detectada: {phrase}")
                return False
        return True

    @staticmethod
    def get_safe_fallback(context: str = "início") -> str:
        """
        Retorna uma resposta segura baseada no contexto
        """
        fallbacks = {
            "início": "Olá! Aqui é Marina Campelo, do Náutico! Qual é seu nome para eu te atender melhor?",
            "nome_coletado": "Perfeito! Hoje no programa Sócio Mais Fiel do Nordeste temos vários planos incríveis. Há quanto tempo você torce para o Náutico?",
            "valor_coletado": "Excelente! Vejo que você tem paixão pelo Náutico. Vou te mostrar como fazer parte da nossa família de sócios!",
            "default": "Como posso ajudar você a apoiar o Náutico na campanha de acesso à Série B?"
        }
        return fallbacks.get(context, fallbacks["default"])


response_formatter = ResponseFormatter()
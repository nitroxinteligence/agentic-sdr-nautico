"""
Response Formatter - Garante formatação correta das respostas
Adiciona tags <RESPOSTA_FINAL> automaticamente quando necessário
"""

import re
from app.utils.logger import emoji_logger


class ResponseFormatter:
    """
    Formata e valida respostas do agente
    Garante que todas as respostas tenham tags <RESPOSTA_FINAL>
    """

    @staticmethod
    def ensure_response_tags(response: str) -> str:
        """
        Garante que a resposta tenha tags <RESPOSTA_FINAL>
        IMPORTANTE: NÃO processa respostas que contêm tools
        """
        if not response:
            return (
                "<RESPOSTA_FINAL>Oi! Como posso ajudar você com energia solar? "
                "☀️</RESPOSTA_FINAL>"
            )
        
        # CRÍTICO: Detecta se a resposta contém uma tool e NÃO a processa
        tool_pattern = r'\[\w+[:\.].*?\]'
        if re.search(tool_pattern, response):
            emoji_logger.system_debug("🔧 Tool detectada na resposta - não adicionando tags RESPOSTA_FINAL")
            return response

        has_opening = "<RESPOSTA_FINAL>" in response
        has_closing = "</RESPOSTA_FINAL>" in response

        if has_opening and has_closing:
            emoji_logger.system_debug("✅ Tags já presentes na resposta")
            return response

        if "RESPOSTA_FINAL" in response.upper():
            emoji_logger.system_warning(
                "⚠️ Tags com formatação incorreta - corrigindo"
            )
            patterns = [
                r'<RESPOSTA[_ ]?FINAL>(.*?)</RESPOSTA[_ ]?FINAL>',
                r'RESPOSTA[_ ]?FINAL[:\s]+(.*?)(?:\n\n|$)',
                r'\[RESPOSTA[_ ]?FINAL\](.*?)\[/RESPOSTA[_ ]?FINAL\]'
            ]
            for pattern in patterns:
                match = re.search(
                    pattern, response, re.DOTALL | re.IGNORECASE
                )
                if match:
                    content = match.group(1).strip()
                    return f"<RESPOSTA_FINAL>{content}</RESPOSTA_FINAL>"

        emoji_logger.system_warning(
            "🔧 Tags ausentes - adicionando automaticamente"
        )
        clean_response = response.strip()
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

        if not clean_response or len(clean_response) < 10:
            emoji_logger.system_error(
                "ResponseFormatter",
                "Resposta vazia após limpeza - usando fallback"
            )
            clean_response = (
                "Oi! Tudo bem? Me chamo Helen Vieira, sou consultora da "
                "Solarprime. Como posso te chamar?"
            )

        formatted = f"<RESPOSTA_FINAL>{clean_response}</RESPOSTA_FINAL>"
        emoji_logger.system_success(
            f"✅ Resposta formatada com tags: {len(formatted)} chars"
        )
        return formatted

    @staticmethod
    def validate_response_content(response: str) -> bool:
        """
        Valida se o conteúdo da resposta está adequado
        """
        match = re.search(
            r'<RESPOSTA_FINAL>(.*?)</RESPOSTA_FINAL>', response, re.DOTALL
        )
        if not match:
            return False

        content = match.group(1).strip()
        if not content:
            emoji_logger.system_error(
                "ResponseFormatter", "Conteúdo vazio dentro das tags"
            )
            return False

        if len(content) < 5:
            emoji_logger.system_error(
                "ResponseFormatter", f"Conteúdo muito curto: {content}"
            )
            return False

        if re.match(r'^[\s\d\W]+$', content):
            emoji_logger.system_error(
                "ResponseFormatter", "Conteúdo sem texto válido"
            )
            return False

        forbidden_phrases = [
            "vou analisar", "processando", "calculando",
            "verificando", "aguarde", "só um momento", "um minutinho"
        ]
        content_lower = content.lower()
        for phrase in forbidden_phrases:
            if phrase in content_lower:
                emoji_logger.system_warning(
                    f"⚠️ Frase proibida detectada: {phrase}"
                )
                return False
        return True

    @staticmethod
    def get_safe_fallback(context: str = "início") -> str:
        """
        Retorna uma resposta segura baseada no contexto
        """
        fallbacks = {
            "início": (
                "Oi! Tudo bem? Me chamo Helen Vieira, sou consultora da "
                "Solarprime e irei realizar o seu atendimento. Antes de "
                "começarmos, como posso te chamar?"
            ),
            "nome_coletado": (
                "Perfeito! Hoje na Solarprime temos 4 modelos de soluções "
                "energéticas. Qual valor você paga atualmente na sua conta de luz?"
            ),
            "valor_coletado": (
                "Excelente! Com esse valor consigo uma economia muito "
                "interessante para você. Podemos agendar uma conversa rápida "
                "para eu te mostrar os números?"
            ),
            "default": "Como posso ajudar você com energia solar hoje? ☀️"
        }
        response = fallbacks.get(context, fallbacks["default"])
        return f"<RESPOSTA_FINAL>{response}</RESPOSTA_FINAL>"


response_formatter = ResponseFormatter()
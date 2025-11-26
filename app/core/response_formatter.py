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
    def replace_placeholders(response: str, lead_info: dict) -> str:
        """
        CRÍTICO: Substitui placeholders por valores reais do lead
        Garante que NUNCA enviamos placeholders para o usuário
        """
        if not response:
            return response

        # Extrair nome do lead
        name = lead_info.get("name", "")

        # Se não tem nome válido, não fazer substituição (evitar bugs)
        if not name or name in ["Lead Náutico", "Usuário Náutico", "Cliente Náutico"]:
            # Se encontrar placeholder sem nome válido, remover a frase inteira
            if "[nome]" in response.lower():
                emoji_logger.system_warning(
                    f"⚠️ PLACEHOLDER DETECTADO SEM NOME VÁLIDO - Removendo menções"
                )
                # Remover padrões comuns com placeholder
                response = re.sub(r',?\s*\[nome\]', '', response, flags=re.IGNORECASE)
                response = re.sub(r'Oi,?\s*\[nome\][!,.\s]*', 'Oi! ', response, flags=re.IGNORECASE)
                response = re.sub(r'Olá,?\s*\[nome\][!,.\s]*', 'Olá! ', response, flags=re.IGNORECASE)
                response = re.sub(r'Desculpe,?\s*\[nome\][!,.\s]*', 'Desculpe! ', response, flags=re.IGNORECASE)
                return response.strip()
            return response

        # Substituir todos os placeholders pelo nome real
        original_response = response

        # Padrões de placeholder a substituir
        placeholder_patterns = [
            (r'\[nome\]', name),
            (r'\{nome\}', name),
            (r'\$nome', name),
            (r'<nome>', name),
        ]

        for pattern, replacement in placeholder_patterns:
            response = re.sub(pattern, replacement, response, flags=re.IGNORECASE)

        # Log se houve substituição
        if response != original_response:
            emoji_logger.system_success(
                f"✅ Placeholders substituídos por '{name}'"
            )

        return response

    @staticmethod
    def ensure_response_tags(response: str, lead_info: dict = None) -> str:
        """
        Processa resposta e remove tags desnecessárias
        Retorna texto limpo e direto
        """
        if not response:
            return "Olá! Aqui é Laura, do Náutico! Como posso te ajudar?"

        # CRÍTICO: Detecta se a resposta contém uma tool e NÃO a processa
        tool_pattern = r'\[\w+[:\.].*?\]'
        if re.search(tool_pattern, response):
            emoji_logger.system_debug("🔧 Tool detectada na resposta - não processando")
            return response

        # PASSO 1: SUBSTITUIR PLACEHOLDERS POR VALORES REAIS (ANTES DE QUALQUER LIMPEZA)
        if lead_info:
            response = ResponseFormatter.replace_placeholders(response, lead_info)

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

        # Sanitize geral: remover markdown e listas/enumerações visíveis
        # Remover code fences e backticks
        clean_response = clean_response.replace('```', '')
        clean_response = clean_response.replace('`', '')

        # Remover cabeçalhos markdown (##, ###, etc.) no início das linhas
        clean_response = re.sub(r'(?m)^\s*#{1,6}\s*', '', clean_response)

        # Remover bullets e enumerações no início das linhas
        def _strip_list_enumerations(text: str) -> str:
            lines = text.splitlines()
            cleaned_lines = []
            for ln in lines:
                l = re.sub(r'^\s*[-*•]\s+', '', ln)               # -, *, •
                l = re.sub(r'^\s*\(?\d+\)?[\.|\)|-]\s+', '', l)  # 1., 1), (1) -
                l = re.sub(r'^\s*[a-zA-Z]\)\s+', '', l)            # a), A)
                # Remover linhas que são apenas enumeradores (ex.: "1.", "a)" ou "II")
                if re.match(r'^\s*(\d+|[ivxlcdmIVXLCDM]+|[a-zA-Z])[\.|\)|-]?\s*$', l):
                    l = ''
                cleaned_lines.append(l.strip())
            # Remover linhas vazias consecutivas
            result = '\n'.join([cl for cl in cleaned_lines if cl])
            result = re.sub(r'\n{3,}', '\n\n', result)
            return result

        clean_response = _strip_list_enumerations(clean_response)

        # Remover ênfases Markdown inline: *texto*, **texto**, _texto_, __texto__
        clean_response = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', clean_response)
        clean_response = re.sub(r'_{1,3}(.+?)_{1,3}', r'\1', clean_response)

        # Substituir traços isolados que simulam bullet dentro da linha
        clean_response = re.sub(r'\s-\s', ' ', clean_response)

        # Garantir pontuação final natural
        if clean_response and not re.search(r'[\.!?]$', clean_response.strip()):
            clean_response = clean_response.strip() + '.'

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
            "início": "Olá! Aqui é Laura, do Náutico! Qual é seu nome para eu te atender melhor?",
            "nome_coletado": "Perfeito! Hoje no programa Sócio Mais Fiel do Nordeste temos vários planos incríveis. Há quanto tempo você torce para o Náutico?",
            "valor_coletado": "Excelente! Vejo que você tem paixão pelo Náutico. Vou te mostrar como fazer parte da nossa família de sócios!",
            "default": "Como posso ajudar você a apoiar o Náutico na campanha de acesso à Série B?"
        }
        return fallbacks.get(context, fallbacks["default"])


response_formatter = ResponseFormatter()
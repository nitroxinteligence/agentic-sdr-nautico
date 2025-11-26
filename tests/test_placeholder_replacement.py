"""
Testes para validar a substituição de placeholders por nomes reais
Garante que o sistema NUNCA envia placeholders para os usuários
"""

import pytest
from app.core.response_formatter import ResponseFormatter


class TestPlaceholderReplacement:
    """Testes de substituição de placeholders"""

    def setup_method(self):
        """Setup para cada teste"""
        self.formatter = ResponseFormatter()
        self.lead_info_with_name = {
            "name": "Diego",
            "phone_number": "5581999999999"
        }
        self.lead_info_without_name = {
            "name": None,
            "phone_number": "5581999999999"
        }
        self.lead_info_generic_name = {
            "name": "Lead Náutico",
            "phone_number": "5581999999999"
        }

    def test_replace_placeholder_brackets(self):
        """Testa substituição de [nome]"""
        response = "Oi, [nome]! Como posso te ajudar?"
        result = self.formatter.replace_placeholders(response, self.lead_info_with_name)

        assert "[nome]" not in result.lower()
        assert "Diego" in result
        assert result == "Oi, Diego! Como posso te ajudar?"

    def test_replace_placeholder_curly_braces(self):
        """Testa substituição de {nome}"""
        response = "Olá, {nome}! Bem-vindo ao Náutico"
        result = self.formatter.replace_placeholders(response, self.lead_info_with_name)

        assert "{nome}" not in result.lower()
        assert "Diego" in result
        assert result == "Olá, Diego! Bem-vindo ao Náutico"

    def test_replace_placeholder_dollar(self):
        """Testa substituição de $nome"""
        response = "Prazer, $nome!"
        result = self.formatter.replace_placeholders(response, self.lead_info_with_name)

        assert "$nome" not in result.lower()
        assert "Diego" in result
        assert result == "Prazer, Diego!"

    def test_replace_placeholder_angle_brackets(self):
        """Testa substituição de <nome>"""
        response = "Massa, <nome>! Vamos conversar?"
        result = self.formatter.replace_placeholders(response, self.lead_info_with_name)

        assert "<nome>" not in result.lower()
        assert "Diego" in result
        assert result == "Massa, Diego! Vamos conversar?"

    def test_remove_placeholder_without_name(self):
        """Testa remoção de placeholder quando não há nome válido"""
        response = "Oi, [nome]! Como posso te ajudar?"
        result = self.formatter.replace_placeholders(response, self.lead_info_without_name)

        # Placeholder deve ser removido
        assert "[nome]" not in result.lower()
        # Frase deve estar limpa
        assert result == "Oi! Como posso te ajudar?"

    def test_remove_placeholder_with_generic_name(self):
        """Testa remoção de placeholder quando há nome genérico"""
        response = "Desculpe, [nome]! Não entendi"
        result = self.formatter.replace_placeholders(response, self.lead_info_generic_name)

        # Placeholder deve ser removido
        assert "[nome]" not in result.lower()
        # Nome genérico não deve aparecer
        assert "Lead Náutico" not in result
        assert result == "Desculpe! Não entendi"

    def test_multiple_placeholders_same_response(self):
        """Testa substituição de múltiplos placeholders na mesma resposta"""
        response = "Oi [nome], tudo bem [nome]? Prazer em te conhecer, [nome]!"
        result = self.formatter.replace_placeholders(response, self.lead_info_with_name)

        # Todos os placeholders devem ser substituídos
        assert "[nome]" not in result.lower()
        assert result.count("Diego") == 3
        assert result == "Oi Diego, tudo bem Diego? Prazer em te conhecer, Diego!"

    def test_case_insensitive_replacement(self):
        """Testa substituição case-insensitive"""
        response = "Olá [NOME], bem-vindo [Nome]! Prazer, [nome]!"
        result = self.formatter.replace_placeholders(response, self.lead_info_with_name)

        # Todos os placeholders devem ser substituídos independente do case
        assert "[nome]" not in result.lower()
        assert result.count("Diego") == 3

    def test_no_placeholders(self):
        """Testa resposta sem placeholders"""
        response = "Olá! Como posso te ajudar hoje?"
        result = self.formatter.replace_placeholders(response, self.lead_info_with_name)

        # Resposta deve permanecer igual
        assert result == response

    def test_empty_response(self):
        """Testa resposta vazia"""
        response = ""
        result = self.formatter.replace_placeholders(response, self.lead_info_with_name)

        assert result == ""

    def test_ensure_response_tags_with_placeholder(self):
        """Testa ensure_response_tags com placeholder"""
        response = "Oi, [nome]! Bem-vindo ao **Náutico**!"
        result = self.formatter.ensure_response_tags(response, self.lead_info_with_name)

        # Placeholder deve ser substituído
        assert "[nome]" not in result.lower()
        assert "Diego" in result
        # Markdown deve ser removido
        assert "**" not in result

    def test_ensure_response_tags_without_lead_info(self):
        """Testa ensure_response_tags sem lead_info"""
        response = "Olá! Como posso te ajudar?"
        result = self.formatter.ensure_response_tags(response)

        # Resposta deve ser processada normalmente
        assert result == "Olá! Como posso te ajudar?"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

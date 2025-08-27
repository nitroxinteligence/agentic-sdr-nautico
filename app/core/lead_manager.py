"""
Lead Manager - Gerenciamento SIMPLES de leads
ZERO complexidade, funcionalidade total
"""

from typing import Dict, Any, Optional, List
import re
from app.utils.logger import emoji_logger
from app.config import settings


class LeadManager:
    """
    Gerenciador de SIMPLES leads e qualificação
    Mantém toda a lógica de extração e scoring
    """

    def __init__(self):
        self.is_initialized = False
        self.scoring_enabled = settings.enable_lead_scoring

    def initialize(self):
        """Inicialização simples"""
        if self.is_initialized:
            return

        emoji_logger.system_ready("📊 LeadManager inicializado")
        self.is_initialized = True

    def extract_lead_info(
            self,
            messages: List[Dict[str, Any]],
            existing_lead_info: Optional[Dict[str, Any]] = None,
            context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extrai e consolida informações do lead de forma robusta,
        processando todo o histórico para garantir a captura de dados essenciais.
        """
        # Começa com uma cópia segura do lead existente ou um novo dicionário.
        lead_info = existing_lead_info.copy() if existing_lead_info else {}

        # Garante que a estrutura de dados mínima sempre exista.
        lead_info.setdefault("name", None)
        lead_info.setdefault("phone_number", None)
        lead_info.setdefault("email", None)
        lead_info.setdefault("bill_value", None)
        lead_info.setdefault("qualification_score", 0)
        lead_info.setdefault("current_stage", "INITIAL_CONTACT")
        lead_info.setdefault("chosen_flow", None)
        lead_info.setdefault("preferences", {}).setdefault("interests", [])
        lead_info.setdefault("preferences", {}).setdefault("objections", [])

        # Itera sobre TODAS as mensagens para preencher informações que ainda estão faltando.
        for msg in messages:
            content_data = msg.get("content", "")
            text_content = ""
            if isinstance(content_data, list):
                for part in content_data:
                    if part.get("type") == "text":
                        text_content = part.get("text", "")
                        break
            elif isinstance(content_data, str):
                text_content = content_data

            content_lower = text_content.lower()
            
            if msg.get("role") == "user":
                # Tenta extrair cada informação apenas se ela ainda não existir no lead_info.
                if not lead_info.get("name"):
                    # Passa o contexto para extração contextual de nomes
                    current_stage = context.get('conversation_stage') if context else None
                    name = self._extract_name(content_lower, current_stage)
                    if name:
                        lead_info["name"] = name
                        emoji_logger.system_debug(f"Nome extraído do histórico: '{name}'")

                if not lead_info.get("email"):
                    email = self._extract_email(content_lower)
                    if email:
                        lead_info["email"] = email
                        emoji_logger.system_debug(f"Email extraído do histórico: '{email}'")

                if not lead_info.get("bill_value"):
                    value = self._extract_bill_value(content_lower)
                    if value:
                        lead_info["bill_value"] = value
                        emoji_logger.system_debug(f"Valor da conta extraído do histórico: '{value}'")

            if not lead_info.get("chosen_flow"):
                chosen_flow = self._extract_chosen_flow(content_lower)
                if chosen_flow:
                    lead_info["chosen_flow"] = chosen_flow
                    emoji_logger.system_debug(f"Fluxo escolhido detectado no histórico: '{chosen_flow}'")

        if self.scoring_enabled:
            lead_info["qualification_score"] = self.calculate_qualification_score(lead_info)
            lead_info["current_stage"] = self.determine_stage(lead_info)

        return lead_info

    def calculate_qualification_score(
            self,
            lead_info: Dict[str, Any],
    ) -> int:
        """Calcula score de qualificação SIMPLES"""
        score = 0.0
        bill_value = lead_info.get("bill_value", 0)
        if bill_value:
            if bill_value >= 1000:
                score += 40
            elif bill_value >= 700:
                score += 30
            elif bill_value >= 500:
                score += 20
            elif bill_value >= 300:
                score += 10

        if lead_info.get("name"):
            score += 10
        if lead_info.get("phone_number"):
            score += 10
        if lead_info.get("email"):
            score += 5
        if lead_info.get("preferences", {}).get("location"):
            score += 5

        property_type = lead_info.get(
            "preferences", {}
        ).get("property_type")
        if property_type:
            if "comercial" in property_type or "empresa" in property_type:
                score += 15
            elif "residencial" in property_type or "casa" in property_type:
                score += 10

        interests = lead_info.get("preferences", {}).get("interests", [])
        if len(interests) >= 3:
            score += 10
        elif len(interests) >= 2:
            score += 7
        elif len(interests) >= 1:
            score += 5

        objections = lead_info.get("preferences", {}).get("objections", [])
        if len(objections) >= 3:
            score -= 5
        elif len(objections) >= 2:
            score -= 3

        return int(max(0, min(100, score)))

    def determine_stage(self, lead_info: Dict[str, Any]) -> str:
        """Determina estágio do lead no funil"""
        score = lead_info.get("qualification_score", 0)
        if score >= 80:
            return "HOT"
        elif score >= 60:
            return "WARM"
        elif score >= 40:
            return "QUALIFYING"
        elif score >= 20:
            return "INTERESTED"
        else:
            return "INITIAL_CONTACT"

    def _extract_name(self, text: str, current_stage: Optional[str] = None) -> Optional[str]:
        """Extrai nome do texto com foco em padrões explícitos e contextuais."""
        emoji_logger.system_debug(f"Iniciando extração de nome. Estágio: {current_stage}, Texto: '{text[:50]}...'")
        
        # Padrões explícitos tradicionais
        patterns = [
            r"meu\s+nome\s+[eé]\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,3})",
            r"me\s+chamo\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,3})",
            r"pode\s+me\s+chamar\s+de\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,3})",
            r"(?:eu\s+)?sou\s+o\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,3})",
            r"(?:eu\s+)?sou\s+a\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){0,3})",
        ]
        
        emoji_logger.system_debug("Testando padrões explícitos de nome")
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_name = match.group(1).strip().title()
                emoji_logger.system_debug(f"Padrão {i+1} encontrou: '{potential_name}'")
                if self._is_valid_name(potential_name):
                    emoji_logger.system_success(f"Nome extraído via padrão explícito: '{potential_name}'")
                    return potential_name
                else:
                    emoji_logger.system_debug(f"Nome rejeitado pela validação: '{potential_name}'")
        
        # Extração contextual: se estamos no estágio de coleta de nome,
        # tentamos capturar nomes isolados com maior flexibilidade
        if current_stage == "estagio_0_coleta_nome":
            emoji_logger.system_debug("Usando extração isolada para estágio de coleta de nome")
            isolated_name = self._extract_isolated_name(text)
            if isolated_name:
                emoji_logger.system_success(f"Nome extraído via método isolado: '{isolated_name}'")
                return isolated_name
            else:
                emoji_logger.system_debug("Método isolado não encontrou nome válido")
        
        emoji_logger.system_warning("Nenhum nome foi extraído do texto")
        return None

    def _extract_isolated_name(self, text: str) -> Optional[str]:
        """Extrai nomes isolados quando estamos no contexto de coleta de nome."""
        emoji_logger.system_debug(f"Tentando extrair nome isolado de: '{text}'")
        
        # Remove pontuação e divide em palavras
        words = re.findall(r'\b[A-ZÀ-ÿ][a-zà-ÿ]{1,}\b', text)
        emoji_logger.system_debug(f"Palavras encontradas: {words}")
        
        for word in words:
            emoji_logger.system_debug(f"Validando palavra: '{word}'")
            if self._is_valid_isolated_name(word):
                name = word.title()
                emoji_logger.system_success(f"Nome isolado capturado: '{name}' no estágio de coleta")
                return name
            else:
                emoji_logger.system_debug(f"Palavra rejeitada: '{word}'")
        
        emoji_logger.system_debug("Nenhum nome isolado válido encontrado")
        return None
    
    def _is_valid_isolated_name(self, name: str) -> bool:
        """Valida se uma palavra isolada pode ser um nome no contexto de coleta."""
        emoji_logger.system_debug(f"Validando nome isolado: '{name}'")
        
        if not name or len(name) < 2 or len(name) > 30:
            emoji_logger.system_debug(f"Nome rejeitado por tamanho: {len(name) if name else 0} caracteres")
            return False
        
        # Lista mais restritiva para nomes isolados
        blacklist = [
            'oi', 'ola', 'sim', 'nao', 'ok', 'tudo', 'bem', 'bom', 'dia', 
            'tarde', 'noite', 'quero', 'gostaria', 'preciso', 'pode', 'claro',
            'conta', 'valor', 'energia', 'obrigado', 'obrigada', 'tchau', 
            'ate', 'logo', 'falar', 'conversar', 'legal', 'show', 'perfeito'
        ]
        
        name_lower = name.lower()
        in_blacklist = name_lower in blacklist
        is_alpha = name.isalpha()
        
        emoji_logger.system_debug(
            f"Validação - Blacklist: {in_blacklist}, Apenas letras: {is_alpha}, "
            f"Resultado: {not in_blacklist and is_alpha}"
        )
        
        return not in_blacklist and is_alpha
    
    def _is_valid_name(self, name: str) -> bool:
        """Valida se uma string é um nome próprio provável."""
        if not name or len(name) < 3 or len(name) > 60:
            return False
        words = name.split()
        if len(words) > 4:
            return False
        blacklist = [
            'a', 'o', 'e', 'de', 'do', 'da', 'dos', 'das', 'com', 'em',
            'para', 'por', 'oi', 'ola', 'sim', 'nao', 'ok', 'tudo', 'bem',
            'bom', 'dia', 'tarde', 'noite', 'quero', 'gostaria', 'preciso',
            'pode', 'claro', 'conta', 'valor', 'energia'
        ]
        for word in words:
            word_lower = word.lower()
            if word_lower in blacklist or not word.isalpha() or len(word) < 2:
                return False
        return True

    def _extract_email(self, text: str) -> Optional[str]:
        """Extrai email do texto"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0).lower() if match else None

    def _extract_bill_value(self, text: str) -> Optional[float]:
        """Extrai valor da conta do texto"""
        emoji_logger.system_debug(f"Extraindo valor da conta de: '{text[:50]}...'")
        
        patterns = [
            r"conta.{0,20}R?\s*\$?\s*(\d+(?:[.,]\d{0,2})?)",
            r"pago.{0,20}R?\s*\$?\s*(\d+(?:[.,]\d{0,2})?)",
            r"valor.{0,20}R?\s*\$?\s*(\d+(?:[.,]\d{0,2})?)",
            r"(\d+(?:[.,]\d{0,2})?)\s*reais",
            r"uns\s*(\d+(?:[.,]\d{0,2})?)",
            r"R?\s*\$?\s*(\d+(?:[.,]\d{0,2})?)"
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                emoji_logger.system_debug(f"Padrão {i+1} encontrou valores: {matches}")
                try:
                    values = [float(m.replace(",", ".")) for m in matches]
                    reasonable_values = [v for v in values if 50 <= v <= 10000]
                    emoji_logger.system_debug(f"Valores razoáveis filtrados: {reasonable_values}")
                    if reasonable_values:
                        final_value = max(reasonable_values)
                        emoji_logger.system_success(f"Valor da conta extraído: R$ {final_value}")
                        return final_value
                except Exception as e:
                    emoji_logger.system_debug(f"Erro ao processar valores: {e}")
        
        emoji_logger.system_debug("Nenhum valor de conta encontrado")
        return None

    def _extract_property_type(self, text: str) -> Optional[str]:
        """Extrai tipo de imóvel"""
        types = {
            "casa": ["casa", "residência", "moradia"],
            "apartamento": ["apartamento", "apto", "ap"],
            "comercial": ["empresa", "comércio", "loja", "escritório"],
            "rural": ["fazenda", "sítio", "chácara", "rural"]
        }
        for prop_type, keywords in types.items():
            if any(keyword in text for keyword in keywords):
                return prop_type
        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """Extrai localização"""
        patterns = [
            r"moro em ([A-Za-z\s]+)", r"sou de ([A-Za-z\s]+)",
            r"estou em ([A-Za-z\s]+)", r"cidade de ([A-Za-z\s]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
        return None

    def _extract_interests(self, text: str) -> List[str]:
        """Extrai interesses demonstrados"""
        interests = []
        interest_keywords = {
            "economia": ["economizar", "economia", "reduzir conta"],
            "sustentabilidade": ["sustentável", "meio ambiente", "verde"],
            "investimento": ["investimento", "retorno", "valorização"],
            "independência": ["independência", "própria energia"],
            "tecnologia": ["tecnologia", "inovação", "moderno"]
        }
        for interest, keywords in interest_keywords.items():
            if any(keyword in text for keyword in keywords):
                interests.append(interest)
        return interests

    def _extract_objections(self, text: str) -> List[str]:
        """Extrai objeções mencionadas"""
        objections = []
        objection_keywords = {
            "preço": ["caro", "muito dinheiro", "não tenho"],
            "desconfiança": ["golpe", "enganação", "não confio"],
            "tempo": ["não é hora", "depois", "mais tarde"],
            "propriedade": ["aluguel", "não é meu", "alugado"],
            "dúvidas": ["não entendo", "complicado", "difícil"]
        }
        for objection, keywords in objection_keywords.items():
            if any(keyword in text for keyword in keywords):
                objections.append(objection)
        return objections

    def _extract_chosen_flow(self, text: str) -> Optional[str]:
        """
        Extrai a escolha de fluxo do usuário com lógica de prioridade para
        evitar falsos positivos.
        """
        text_lower = text.lower().strip()
        emoji_logger.system_debug(f"Extraindo fluxo escolhido de: '{text_lower}'")

        # Mapeamento com palavras-chave/sinônimos para cada fluxo.
        # A ordem aqui é importante: do mais específico/prioritário para o mais geral.
        # IMPORTANTE: Palavras-chave devem ser específicas para evitar falsos positivos
        flow_priority_map = {
            "Usina Investimento": ["usina de investimento", "usina investimento", "opção 4", "modelo 4"],
            "Aluguel de Lote": ["aluguel de lote", "alugar lote", "opção 2", "modelo 2"],
            "Compra com Desconto": ["compra de energia", "comprar energia", "desconto", "opção 3", "modelo 3"],
            "Instalação Usina Própria": ["instalação", "usina própria", "minha usina", "opção 1", "modelo 1"],
        }

        for flow, keywords in flow_priority_map.items():
            emoji_logger.system_debug(f"Testando fluxo '{flow}' com palavras-chave: {keywords}")
            for keyword in keywords:
                # Usamos \b para garantir que estamos combinando palavras inteiras e evitar
                # que "investimento" combine com "pré-investimento", por exemplo.
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    emoji_logger.system_success(f"Fluxo escolhido detectado: '{flow}' via palavra-chave '{keyword}'")
                    return flow
        
        emoji_logger.system_debug("Nenhum fluxo específico detectado")
        return None

    def format_lead_summary(self, lead_info: Dict[str, Any]) -> str:
        """Formata resumo do lead para exibição"""
        summary = "📊 **Resumo do Lead**\n\n"
        if lead_info.get("name"):
            summary += f"👤 Nome: {lead_info['name']}\n"
        if lead_info.get("phone"):
            summary += f"📱 Telefone: {lead_info['phone']}\n"
        if lead_info.get("email"):
            summary += f"📧 Email: {lead_info['email']}\n"
        if lead_info.get("location"):
            summary += f"📍 Localização: {lead_info['location']}\n"
        if lead_info.get("bill_value"):
            summary += f"💰 Valor da conta: R$ {lead_info['bill_value']:.2f}\n"
        if lead_info.get("property_type"):
            summary += f"🏠 Tipo de imóvel: {lead_info['property_type']}\n"
        if lead_info.get("interests"):
            summary += f"✨ Interesses: {', '.join(lead_info['interests'])}\n"
        if lead_info.get("objections"):
            summary += f"⚠️ Objeções: {', '.join(lead_info['objections'])}\n"
        if lead_info.get("chosen_flow"):
            summary += f"🎯 Fluxo escolhido: {lead_info['chosen_flow']}\n"
        if self.scoring_enabled:
            summary += (
                f"\n🎯 Score: {lead_info['qualification_score']:.0f}/100\n"
                f"📈 Estágio: {lead_info['stage'].upper()}\n"
            )
        return summary
"""
Context Analyzer - Análise SIMPLES de contexto e emoções
ZERO complexidade, funcionalidade total
"""
import re
from typing import Dict, Any, List
from app.utils.logger import emoji_logger
from app.config import settings


class ContextAnalyzer:
    """
    Analisador SIMPLES de contexto e estado emocional
    Mantém toda a inteligência de análise conversacional
    """

    def __init__(self):
        self.is_initialized = False
        self.context_enabled = settings.enable_context_analysis
        self.sentiment_enabled = settings.enable_sentiment_analysis
        self.emotional_enabled = settings.enable_emotional_triggers

    def initialize(self):
        """Inicialização simples"""
        if self.is_initialized:
            return
        emoji_logger.system_ready("🧠 ContextAnalyzer inicializado")
        self.is_initialized = True

    def _get_text_from_message(self, msg: Dict[str, Any]) -> str:
        """Helper para extrair texto de forma segura de uma mensagem."""
        content = msg.get("content", "")
        if isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    return part.get("text", "")
            return ""
        return str(content)

    def analyze_context(self,
                        messages: List[Dict[str, Any]],
                        lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa contexto da conversa de forma INTELIGENTE e CONTEXTUAL
        Fornece informações ricas para extração de nomes e tomada de decisões
        """
        current_message_text = self._get_text_from_message(messages[-1]) if messages else ""
        conversation_stage = self._determine_stage(messages, lead_info)
        
        context = {
            "conversation_stage": conversation_stage,
            "stage_context": self._get_stage_context(conversation_stage, messages, lead_info),
            "user_intent": self._extract_intent(current_message_text),
            "sentiment": self._analyze_sentiment(current_message_text),
            "emotional_state": self._analyze_emotional_state(messages),
            "key_topics": self._extract_topics(messages),
            "urgency_level": self._assess_urgency(current_message_text),
            "engagement_level": self._calculate_engagement(messages),
            "objections_raised": self._find_objections(messages),
            "questions_asked": self._extract_questions(messages),
            "action_needed": self._determine_action(current_message_text),
            "conversation_flow": self._analyze_conversation_flow(messages),
            "name_extraction_hints": self._get_name_extraction_hints(messages, conversation_stage),
            "behavioral_patterns": self._analyze_behavioral_patterns(messages)
        }
        return context

    def _determine_stage(self, messages: List[Dict[str, Any]], lead_info: Dict[str, Any]) -> str:
        """
        Determina o estágio da conversa com base nos dados consolidados do lead_info,
        tornando a lógica mais robusta e menos dependente de análise de texto.
        """
        # A fonte da verdade agora são os dados do lead, não o texto da conversa.
        has_name = bool(lead_info.get("name"))
        has_bill_value = bool(lead_info.get("bill_value"))
        has_chosen_flow = bool(lead_info.get("chosen_flow"))

        # Lógica de fluxo baseada em dados, muito mais confiável.
        if not has_name:
            return "estagio_0_coleta_nome"
        
        if not has_bill_value:
            return "estagio_1_qualificacao_por_valor"

        if not has_chosen_flow:
            return "estagio_2_roteamento_e_apresentacao"

        # Se todas as informações principais foram coletadas, estamos na fase de qualificação detalhada.
        # Uma verificação final de intenção de agendamento pode ser útil.
        last_message_text = self._get_text_from_message(messages[-1]) if messages else ""
        if any(keyword in last_message_text for keyword in ["agendar", "marcar", "reunião", "horário"]):
            return "agendamento"

        return "qualificacao_detalhada"

    def _extract_intent(self, message: str) -> str:
        message_lower = message.lower()
        intents = {
            "reagendamento": ["reagendar", "reagende", "remarcar", "mudar o horario", "outro horario"],
            "cancelamento": ["cancelar", "cancela", "nao vou poder", "cancele"],
            "informação": ["quanto", "como", "qual", "quando", "onde", "quem"],
            "interesse": ["quero", "gostaria", "interessado"], "dúvida": ["sera", "nao sei", "talvez"],
            "objeção": ["caro", "dificil", "problema"], "agendamento": ["agendar", "marcar", "reuniao", "reunião"],
            "compra": ["comprar", "adquirir", "fechar"], "reclamação": ["ruim", "pessimo", "horrivel"],
            "elogio": ["otimo", "excelente", "adorei"]
        }
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        return "conversa"

    def _analyze_sentiment(self, message: str) -> Dict[str, Any]:
        if not self.sentiment_enabled: return {"enabled": False}
        message_lower = message.lower()
        pos_words = ["bom", "ótimo", "excelente", "legal", "perfeito", "adorei", "gostei", "sim", "quero"]
        neg_words = ["ruim", "péssimo", "horrível", "não", "nunca", "problema", "difícil", "caro"]
        pos_count = sum(1 for word in pos_words if word in message_lower)
        neg_count = sum(1 for word in neg_words if word in message_lower)
        if pos_count > neg_count: sentiment, score = "positivo", min(1.0, pos_count * 0.2)
        elif neg_count > pos_count: sentiment, score = "negativo", max(-1.0, -neg_count * 0.2)
        else: sentiment, score = "neutro", 0.0
        return {"enabled": True, "sentiment": sentiment, "score": score, "confidence": 0.7}

    def _analyze_emotional_state(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.emotional_enabled: return {"enabled": False}
        emotions = {"frustração": 0, "entusiasmo": 0, "hesitação": 0, "urgência": 0, "confiança": 0}
        for msg in messages[-5:]:
            content = self._get_text_from_message(msg).lower()
            if any(w in content for w in ["demora", "difícil"]): emotions["frustração"] += 1
            if any(w in content for w in ["ótimo", "excelente", "adorei"]): emotions["entusiasmo"] += 1
            if any(w in content for w in ["não sei", "talvez", "pensar"]): emotions["hesitação"] += 1
            if any(w in content for w in ["urgente", "rápido", "agora"]): emotions["urgência"] += 1
            if any(w in content for w in ["confio", "acredito", "certeza"]): emotions["confiança"] += 1
        
        dominant = "neutro"
        intensity = 0.0
        if any(emotions.values()):
            dominant_emotion_key = max(emotions, key=emotions.get)
            if emotions[dominant_emotion_key] > 0:
                dominant = dominant_emotion_key
                intensity = min(1.0, emotions[dominant] * 0.3)

        return {"enabled": True, "dominant": dominant, "scores": emotions, "intensity": intensity}

    def _extract_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        # IMPORTANTE: Palavras-chave devem ser específicas para evitar falsos positivos
        topics, keywords = [], {"economia": ["economizar", "conta", "valor"], "energia_solar": ["solar", "painel", "energia"], "investimento_solar": ["investir em solar", "retorno solar", "custo solar"], "instalação": ["instalar", "obra", "telhado"]}
        all_text = " ".join([self._get_text_from_message(msg) for msg in messages]).lower()
        for topic, keys in keywords.items():
            if any(key in all_text for key in keys):
                topics.append(topic)
        return topics

    def _assess_urgency(self, message: str) -> str:
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["urgente", "agora", "hoje"]): return "alta"
        if any(w in msg_lower for w in ["amanhã", "semana", "breve"]): return "média"
        if any(w in msg_lower for w in ["futuro", "depois", "talvez"]): return "baixa"
        return "normal"

    def _calculate_engagement(self, messages: List[Dict[str, Any]]) -> float:
        if len(messages) < 2: return 0.5
        text_messages = [self._get_text_from_message(m) for m in messages]
        avg_len = sum(len(m) for m in text_messages) / len(messages)
        q_count = sum(1 for m in text_messages if "?" in m)
        factors = {"msg_count": min(1.0, len(messages) / 20), "avg_len": min(1.0, avg_len / 100), "questions": min(1.0, q_count / 5)}
        return sum(factors.values()) / len(factors)

    def _find_objections(self, messages: List[Dict[str, Any]]) -> List[str]:
        objections, patterns = [], {"preço": ["caro", "dinheiro"], "desconfiança": ["golpe", "não confio"], "timing": ["agora não", "depois"], "propriedade": ["aluguel", "não é meu"], "tecnologia": ["complicado", "difícil"]}
        all_text = " ".join([self._get_text_from_message(msg) for msg in messages]).lower()
        for obj, pats in patterns.items():
            if any(p in all_text for p in pats):
                objections.append(obj)
        return objections

    def _extract_questions(self, messages: List[Dict[str, Any]]) -> List[str]:
        questions = []
        for msg in messages:
            content = self._get_text_from_message(msg)
            if "?" in content:
                questions.append(content.strip())
        return questions[-5:]

    def _determine_action(self, message: str) -> str:
        msg_lower = message.lower()
        actions = {"agendar": ["agendar", "marcar", "reunião"], "qualificar": ["conta", "valor", "consumo"], "informar": ["como funciona", "quanto custa", "dúvida"], "fechar": ["quero", "fechar", "contratar"]}
        for action, keys in actions.items():
            if any(key in msg_lower for key in keys):
                return action
        return "conversar"

    def _get_stage_context(self, stage: str, messages: List[Dict[str, Any]], lead_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fornece contexto específico para cada estágio da conversa
        """
        stage_contexts = {
            "estagio_0_coleta_nome": {
                "description": "Coletando nome do lead",
                "expected_info": "nome",
                "conversation_length": len(messages),
                "attempts_made": self._count_name_attempts(messages),
                "resistance_level": self._assess_name_resistance(messages)
            },
            "estagio_1_qualificacao_por_valor": {
                "description": "Qualificando por valor da conta de energia",
                "expected_info": "valor da conta",
                "has_name": bool(lead_info.get("name")),
                "name_quality": self._assess_name_quality(lead_info.get("name", ""))
            },
            "estagio_2_roteamento_e_apresentacao": {
                "description": "Roteamento e apresentação de soluções",
                "expected_info": "escolha de fluxo",
                "collected_data": {
                    "name": lead_info.get("name"),
                    "bill_value": lead_info.get("bill_value")
                }
            },
            "qualificacao_detalhada": {
                "description": "Qualificação detalhada do lead",
                "collected_data": lead_info,
                "next_steps": "agendamento ou mais qualificação"
            },
            "agendamento": {
                "description": "Processo de agendamento",
                "ready_for_scheduling": True,
                "lead_qualified": True
            }
        }
        
        return stage_contexts.get(stage, {"description": "Estágio não identificado"})

    def _count_name_attempts(self, messages: List[Dict[str, Any]]) -> int:
        """
        Conta quantas vezes o sistema tentou coletar o nome
        """
        attempts = 0
        for msg in messages:
            content = self._get_text_from_message(msg).lower()
            if any(phrase in content for phrase in [
                "qual seu nome", "como posso te chamar", "me diga seu nome",
                "qual é o seu nome", "como você se chama"
            ]):
                attempts += 1
        return attempts

    def _assess_name_resistance(self, messages: List[Dict[str, Any]]) -> str:
        """
        Avalia o nível de resistência para fornecer o nome
        """
        resistance_indicators = [
            "não quero falar", "prefiro não dizer", "não precisa saber",
            "só informação", "apenas informação", "não vou falar"
        ]
        
        all_text = " ".join([self._get_text_from_message(msg) for msg in messages]).lower()
        
        if any(indicator in all_text for indicator in resistance_indicators):
            return "alta"
        elif len(messages) > 5 and not any("nome" in self._get_text_from_message(msg).lower() for msg in messages[-3:]):
            return "média"
        else:
            return "baixa"

    def _assess_name_quality(self, name: str) -> Dict[str, Any]:
        """
        Avalia a qualidade do nome coletado
        """
        if not name:
            return {"quality": "none", "confidence": 0.0}
        
        generic_names = ["lead sem nome", "lead", "cliente", "usuário", "pessoa"]
        
        if name.lower() in [g.lower() for g in generic_names]:
            return {"quality": "generic", "confidence": 0.1}
        
        # Verifica se parece um nome real
        if len(name.split()) >= 2 and name.replace(" ", "").isalpha():
            return {"quality": "high", "confidence": 0.9}
        elif name.replace(" ", "").isalpha() and len(name) > 2:
            return {"quality": "medium", "confidence": 0.7}
        else:
            return {"quality": "low", "confidence": 0.3}

    def _analyze_conversation_flow(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa o fluxo da conversa para identificar padrões
        """
        return {
            "total_messages": len(messages),
            "user_messages": len([m for m in messages if m.get("role") == "user"]),
            "assistant_messages": len([m for m in messages if m.get("role") == "assistant"]),
            "conversation_pace": "rápida" if len(messages) > 10 else "normal" if len(messages) > 5 else "lenta",
            "last_user_response_length": len(self._get_text_from_message(messages[-1])) if messages else 0
        }

    def _get_name_extraction_hints(self, messages: List[Dict[str, Any]], stage: str) -> Dict[str, Any]:
        """
        Fornece dicas específicas para extração de nomes baseado no contexto
        """
        hints = {
            "stage_allows_isolated_names": stage == "estagio_0_coleta_nome",
            "conversation_length": len(messages),
            "recent_context": []
        }
        
        # Analisa as últimas 3 mensagens para contexto
        for msg in messages[-3:]:
            content = self._get_text_from_message(msg)
            if any(phrase in content.lower() for phrase in [
                "meu nome", "me chamo", "sou o", "sou a", "eu sou"
            ]):
                hints["recent_context"].append("self_introduction")
            elif "nome" in content.lower():
                hints["recent_context"].append("name_request")
        
        return hints

    def _analyze_behavioral_patterns(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa padrões comportamentais do usuário
        """
        if len(messages) < 2:
            return {"insufficient_data": True}
        
        user_messages = [m for m in messages if m.get("role") == "user"]
        
        return {
            "response_style": self._classify_response_style(user_messages),
            "information_sharing_willingness": self._assess_sharing_willingness(user_messages),
            "engagement_trend": self._calculate_engagement_trend(user_messages),
            "communication_preference": self._identify_communication_preference(user_messages)
        }

    def _classify_response_style(self, user_messages: List[Dict[str, Any]]) -> str:
        """
        Classifica o estilo de resposta do usuário
        """
        if not user_messages:
            return "unknown"
        
        avg_length = sum(len(self._get_text_from_message(m)) for m in user_messages) / len(user_messages)
        
        if avg_length > 50:
            return "verbose"
        elif avg_length > 20:
            return "moderate"
        else:
            return "concise"

    def _assess_sharing_willingness(self, user_messages: List[Dict[str, Any]]) -> str:
        """
        Avalia a disposição do usuário em compartilhar informações
        """
        sharing_indicators = 0
        resistance_indicators = 0
        
        for msg in user_messages:
            content = self._get_text_from_message(msg).lower()
            
            if any(phrase in content for phrase in [
                "meu nome é", "me chamo", "sou o", "minha conta", "pago", "gasto"
            ]):
                sharing_indicators += 1
            
            if any(phrase in content for phrase in [
                "não quero", "prefiro não", "não precisa", "só informação"
            ]):
                resistance_indicators += 1
        
        if sharing_indicators > resistance_indicators:
            return "high"
        elif resistance_indicators > sharing_indicators:
            return "low"
        else:
            return "medium"

    def _calculate_engagement_trend(self, user_messages: List[Dict[str, Any]]) -> str:
        """
        Calcula a tendência de engajamento ao longo da conversa
        """
        if len(user_messages) < 3:
            return "insufficient_data"
        
        # Analisa o comprimento das mensagens ao longo do tempo
        lengths = [len(self._get_text_from_message(m)) for m in user_messages]
        
        if lengths[-1] > lengths[0]:
            return "increasing"
        elif lengths[-1] < lengths[0]:
            return "decreasing"
        else:
            return "stable"

    def _identify_communication_preference(self, user_messages: List[Dict[str, Any]]) -> str:
        """
        Identifica a preferência de comunicação do usuário
        """
        question_count = 0
        statement_count = 0
        
        for msg in user_messages:
            content = self._get_text_from_message(msg)
            if "?" in content:
                question_count += 1
            else:
                statement_count += 1
        
        if question_count > statement_count:
            return "inquisitive"
        else:
            return "responsive"

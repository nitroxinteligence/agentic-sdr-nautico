"""
AgenticSDR Stateless - Arquitetura ZERO complexidade para produção
Cada requisição é completamente isolada e independente
Não há estado compartilhado entre conversas
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pytz
import re
import traceback

from app.integrations.supabase_client import supabase_client
from app.core.model_manager import ModelManager
from app.core.multimodal_processor import MultimodalProcessor
from app.core.lead_manager import LeadManager
from app.core.context_analyzer import ContextAnalyzer
from app.services.conversation_monitor import get_conversation_monitor
from app.utils.logger import emoji_logger
from app.core.response_formatter import response_formatter
from app.utils.time_utils import get_period_of_day
from app.config import settings

# Importar serviços e wrappers
from app.services.calendar_service_100_real import CalendarServiceReal
from app.services.crm_service_100_real import CRMServiceReal
from app.services.followup_service_100_real import FollowUpServiceReal
from app.services.knowledge_service import KnowledgeService
from app.services.crm_sync_service import crm_sync_service
from app.services.service_wrappers import (
    CalendarServiceWrapper,
    CRMServiceWrapper,
    FollowUpServiceWrapper,
    KnowledgeServiceWrapper
)
from app.tools.stage_management_tools import StageManagementTools
from app.tools.followup_nautico_tools import FollowUpNauticoTools
from app.services.audio_service import AudioService


class AgenticSDRStateless:
    """
    SDR Agent STATELESS - Cada requisição é isolada
    Sem singleton, sem estado compartilhado
    100% thread-safe e multi-tenant
    """

    def __init__(self):
        """Inicializa apenas os módulos (stateless)"""
        self.model_manager = ModelManager()
        self.multimodal = MultimodalProcessor()
        self.lead_manager = LeadManager()
        self.context_analyzer = ContextAnalyzer()
        self.conversation_monitor = get_conversation_monitor()

        # Instanciar serviços com wrappers condicionais
        calendar_real = CalendarServiceReal() if settings.enable_google_calendar else None
        crm_real = CRMServiceReal() if settings.enable_kommo_crm else None
        followup_real = FollowUpServiceReal() if settings.enable_follow_up_automation else None
        knowledge_real = KnowledgeService() if settings.enable_knowledge_base else None
        
        # Aplicar wrappers condicionais
        self.calendar_service = CalendarServiceWrapper(calendar_real) if calendar_real else None
        self.crm_service = CRMServiceWrapper(crm_real) if crm_real else None
        self.followup_service = FollowUpServiceWrapper(followup_real) if followup_real else None
        self.knowledge_service = KnowledgeServiceWrapper(knowledge_real) if knowledge_real else None

        # Inicializar ferramentas de estágio e follow-up
        self.stage_tools = StageManagementTools(self.crm_service)
        self.followup_nautico_tools = FollowUpNauticoTools(self.followup_service, self.crm_service)
        
        # Inicializar serviço de áudio
        self.audio_service = AudioService()

        self.is_initialized = False

    async def _get_conversation_state(self, lead_info: Dict[str, Any]) -> str:
        """
        Determina estado atual da conversa para controlar fluxo de coleta de nome
        Returns: 'new', 'waiting_name', 'name_collected', 'qualified'
        """
        # Conversa totalmente nova - sem ID
        if not lead_info.get("id"):
            return 'new'
            
        # Lead existe mas sem nome válido - aguardando coleta
        # Inclui nomes genéricos como "Lead Náutico", None, ou strings vazias
        name = lead_info.get("name")
        if (lead_info.get("id") and 
            (not name or 
             name.strip() == "" or 
             name == "Lead Náutico" or
             name == "Usuário Náutico" or
             name == "Cliente Náutico")):
            return 'waiting_name'
            
        # Lead com nome válido coletado
        if (lead_info.get("id") and 
            name and 
            name.strip() and
            name not in ["Lead Náutico", "Usuário Náutico", "Cliente Náutico"]):
            return 'name_collected'
            
        return 'qualified'

    def _extract_name_from_response(self, message: str) -> str:
        """
        Extrai nome quando usuário responde à pergunta "qual seu nome?"
        Com validação rigorosa para evitar nomes inválidos
        """
        import re
        
        # Limpar mensagem
        clean_msg = message.strip().lower()
        
        # Lista de palavras inválidas que não são nomes
        invalid_words = {
            'eu', 'me', 'mim', 'meu', 'minha', 'sim', 'não', 'ok', 'oi', 'olá', 'ola',
            'bem', 'mal', 'bom', 'boa', 'obrigado', 'obrigada', 'valeu', 'brigado',
            'náutico', 'clube', 'time', 'futebol', 'aqui', 'aí', 'lá', 'onde',
            'quando', 'como', 'porque', 'qual', 'quem', 'que', 'o', 'a', 'um', 'uma',
            'este', 'esta', 'esse', 'essa', 'isto', 'isso', 'ele', 'ela', 'eles', 'elas',
            'nós', 'vocês', 'você', 'vc', 'voce', 'tu', 'teu', 'tua', 'seu', 'sua',
            'sou', 'é', 'são', 'estou', 'está', 'estão', 'tem', 'tenho', 'tinha',
            'hello', 'hi', 'dia', 'tarde', 'noite', 'tudo', 'como', 'vai', 'salve', 'fala'
        }
        
        # Padrões de resposta com nome
        patterns = [
            r"(?:meu nome é|me chamo|sou|eu sou|é)\s+([\w\s]{2,30})",
            r"^([\w\s]{2,30})$",  # Só o nome
            r"nome:\s*([\w\s]{2,30})",
            r"(?:eu me chamo|chamo)\s+([\w\s]{2,30})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean_msg, re.IGNORECASE | re.UNICODE)
            if match:
                name = match.group(1).strip().title()
                name_words = name.lower().split()
                
                # Validações rigorosas
                if self._is_valid_name(name, name_words, invalid_words):
                    return name
        
        return None
    
    def _is_valid_name(self, name: str, name_words: list, invalid_words: set) -> bool:
        """
        Valida se o nome extraído é realmente um nome válido
        """
        import re
        
        # 1. Comprimento mínimo e máximo
        if len(name) < 2 or len(name) > 50:
            self._log_name_validation_details(name, f"Comprimento inválido: {len(name)} caracteres")
            return False
            
        # 2. Não pode ser só números
        if name.isdigit():
            self._log_name_validation_details(name, "Contém apenas números")
            return False
            
        # 3. Deve ter pelo menos uma letra
        if not re.search(r'[a-záêôçãõéíúà]', name.lower()):
            self._log_name_validation_details(name, "Não contém letras válidas")
            return False
            
        # 4. Não pode conter caracteres inválidos
        invalid_chars = ['@', '.com', 'www', 'http', '#', '$', '%', '&', '*', '+', '=']
        for char in invalid_chars:
            if char in name.lower():
                self._log_name_validation_details(name, f"Contém caractere inválido: {char}")
                return False
            
        # 5. Verificar palavras inválidas
        invalid_found = [word for word in name_words if word in invalid_words]
        if invalid_found:
            self._log_name_validation_details(name, f"Contém palavras inválidas: {invalid_found}")
            return False
            
        # 6. Não pode ser uma única palavra muito curta (< 3 caracteres)
        if len(name_words) == 1 and len(name) < 3:
            self._log_name_validation_details(name, "Palavra única muito curta")
            return False
            
        # 7. Padrões específicos inválidos
        invalid_patterns = [
            (r'^(eu|me|mim|tu)$', "Pronome pessoal"),
            (r'^(sim|não|ok|oi|olá)$', "Palavra comum não-nome"),
            (r'^(a|o|um|uma|de|da|do)$', "Artigo ou preposição"),
            (r'^\d+$', "Apenas números"),
            (r'^[^a-záêôçãõéíúà]+$', "Sem letras do alfabeto"),
        ]
        
        for pattern, description in invalid_patterns:
            if re.match(pattern, name.lower()):
                self._log_name_validation_details(name, description)
                return False
                
        # 8. Deve parecer um nome brasileiro válido
        # Aceita nomes compostos, mas pelo menos uma palavra deve ter 3+ caracteres
        valid_word_found = False
        for word in name_words:
            if len(word) >= 3 and word.lower() not in invalid_words:
                # Verificar se tem padrão de nome (não é sigla/abreviação)
                if re.match(r'^[a-záêôçãõéíúà]+$', word.lower()):
                    valid_word_found = True
                    break
                    
        if not valid_word_found:
            self._log_name_validation_details(name, "Nenhuma palavra válida encontrada (mín 3 chars)")
            return False
            
        # Se chegou até aqui, é válido
        emoji_logger.system_success(f"✅ Nome validado com sucesso: '{name}'")
        return True
    
    def _log_name_validation_details(self, message: str, reason: str):
        """Log detalhado dos motivos de rejeição de nome"""
        emoji_logger.system_debug(
            f"🚫 Nome rejeitado: '{message}' | Motivo: {reason}"
        )
    
    def _is_initial_greeting(self, message: str) -> bool:
        """
        Verifica se a mensagem é uma saudação inicial
        """
        clean_msg = message.strip().lower()
        
        # Padrões de saudação inicial
        greeting_patterns = [
            r'^olá\.?$', r'^oi\.?$', r'^ola\.?$', r'^hello\.?$', r'^hi\.?$',
            r'^bom dia\.?$', r'^boa tarde\.?$', r'^boa noite\.?$',
            r'^tudo bem\??$', r'^como vai\??$', r'^oi tudo bem\??$',
            r'^olá tudo bem\??$', r'^oi pessoal\.?$', r'^e aí\??$',
            r'^salve\.?$', r'^fala\.?$', r'^eae\.?$', r'^opa\.?$'
        ]
        
        for pattern in greeting_patterns:
            if re.match(pattern, clean_msg):
                emoji_logger.system_debug(f"👋 Saudação detectada: '{message}' matched pattern: {pattern}")
                return True
                
        return False

    async def initialize(self):
        """Inicialização dos módulos assíncronos"""
        if self.is_initialized:
            return

        emoji_logger.system_start("AgenticSDR Stateless")

        try:
            self.model_manager.initialize()
            self.multimodal.initialize()
            self.lead_manager.initialize()
            self.context_analyzer.initialize()
            # TEMPORARIAMENTE DESABILITADO: ConversationMonitor
            # await self.conversation_monitor.initialize()
            
            # Inicializar serviços condicionalmente
            if self.calendar_service:
                try:
                    await self.calendar_service.initialize()
                except Exception as e:
                    emoji_logger.system_warning(
                        f"Falha ao inicializar CalendarService: {e}. "
                        f"O agente continuará sem funcionalidades de calendário."
                    )
            else:
                emoji_logger.system_info("Google Calendar desabilitado via configuração")
                
            if self.crm_service:
                await self.crm_service.initialize()
            else:
                emoji_logger.system_info("CRM Integration desabilitado via configuração")
                
            if self.followup_service:
                await self.followup_service.initialize()
            else:
                emoji_logger.system_info("Follow-up Automation desabilitado via configuração")
                
            if not self.knowledge_service:
                emoji_logger.system_info("Knowledge Base desabilitado via configuração")

            self.is_initialized = True
            emoji_logger.system_ready(
                "✅ AgenticSDR Stateless inicializado!",
                modules=[
                    "ModelManager", "MultimodalProcessor",
                    "LeadManager", "ContextAnalyzer", "CalendarService",
                    "CRMService", "FollowUpService"
                ]
            )

        except Exception as e:
            import traceback
            emoji_logger.system_error(
                "AgenticSDRStateless",
                f"Erro na inicialização: {e}"
            )
            raise

    async def process_message(
            self,
            message: str,
            execution_context: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """
        Processa mensagem com contexto isolado, orquestrando o fluxo de trabalho.
        """
        if not self.is_initialized:
            emoji_logger.system_debug("Inicializando AgenticSDRStateless...")
            await self.initialize()
            emoji_logger.system_success("AgenticSDRStateless inicializado")

        emoji_logger.agentic_start(f"🤖 AGENTE STATELESS INICIADO - Mensagem: '{message[:100]}...'")

        try:
            # Etapa 1: Preparar o contexto da execução
            conversation_history = execution_context.get("conversation_history", [])
            lead_info = execution_context.get("lead_info", {})
            phone = execution_context.get("phone")
            
            emoji_logger.system_debug(
                f"📋 CONTEXTO CARREGADO - Telefone: {phone}, "
                f"Histórico: {len(conversation_history)} msgs, "
                f"Lead: {lead_info.get('name', 'N/A')} (ID: {lead_info.get('id', 'N/A')})"
            )

            # TEMPORARIAMENTE DESABILITADO: ConversationMonitor 
            # emoji_logger.system_debug("Registrando mensagem do usuário...")
            # await self.conversation_monitor.register_message(phone=phone, is_from_user=True, lead_info=lead_info)
            # emoji_logger.system_success("Mensagem do usuário registrada")

            # NOVO: Verificar estado da conversa ANTES de processar
            conversation_state = await self._get_conversation_state(lead_info)
            emoji_logger.system_debug(f"🔄 Estado da conversa: {conversation_state}")
            
            # ETAPA 0a: NOVA CONVERSA - Perguntar nome primeiro
            if conversation_state == 'new':
                emoji_logger.agentic_start("🆕 Nova conversa - perguntando nome antes de criar lead")
                
                response = (
                    "Olá! Aqui é Laura, do Náutico! "
                    "Vi que você demonstrou interesse no clube. "
                    "Qual é seu nome para eu te atender melhor?"
                )
                
                # Criar lead temporário APENAS para manter estado (sem nome ainda)
                temp_lead_data = {
                    "phone_number": phone,
                    "name": None,  # IMPORTANTE: Sem nome ainda
                    "current_stage": "AGUARDANDO_NOME"
                }
                
                try:
                    created_lead = await supabase_client.create_lead(temp_lead_data)
                    lead_info.update(created_lead)
                    emoji_logger.system_success(f"Lead temporário criado: {lead_info.get('id')}")
                except Exception as e:
                    emoji_logger.system_error("AgenticSDRStateless", f"Erro ao criar lead temporário: {e}")
                
                return response, lead_info
            
            # ETAPA 0b: AGUARDANDO NOME - Processar resposta com nome
            elif conversation_state == 'waiting_name':
                emoji_logger.system_debug(f"🔍 Analisando possível nome na mensagem: '{message}'")
                
                # Verificar se é uma saudação inicial (deve reiniciar processo)
                if self._is_initial_greeting(message):
                    emoji_logger.system_debug("👋 Detectada saudação inicial - reiniciando processo de coleta de nome")
                    response = (
                        "Oi! Que bom ter você aqui! 😊 "
                        "Sou a Laura do Náutico. "
                        "Para eu te atender melhor, qual é o seu nome?"
                    )
                    return response, lead_info
                
                extracted_name = self._extract_name_from_response(message)
                
                if extracted_name:
                    emoji_logger.agentic_success(f"👤 Nome coletado com sucesso: {extracted_name}")
                    
                    # Atualizar lead no Supabase com nome
                    await supabase_client.update_lead(lead_info["id"], {
                        "name": extracted_name,
                        "current_stage": "INITIAL_CONTACT"
                    })
                    lead_info["name"] = extracted_name
                    
                    # AGORA SIM: Criar no Kommo CRM com nome real
                    if self.crm_service:
                        try:
                            emoji_logger.system_info(f"🏢 Criando lead '{extracted_name}' no Kommo CRM...")
                            kommo_response = await self.crm_service.create_lead(lead_info)
                            
                            if kommo_response.get("success"):
                                kommo_id = kommo_response.get("lead_id")
                                lead_info["kommo_lead_id"] = kommo_id
                                
                                await supabase_client.update_lead(lead_info["id"], {
                                    "kommo_lead_id": kommo_id
                                })
                                
                                emoji_logger.team_crm(f"✅ Lead '{extracted_name}' criado no Kommo: ID {kommo_id}")
                            else:
                                emoji_logger.system_warning(f"Erro ao criar '{extracted_name}' no Kommo")
                        except Exception as e:
                            emoji_logger.system_error("AgenticSDRStateless", f"Falha ao criar no Kommo: {e}")
                    
                    # AGORA SIM: Enviar áudio personalizado
                    audio_sent = await self._handle_initial_trigger_audio(lead_info, phone, [])
                    
                    # Só enviar resposta se áudio foi enviado com sucesso
                    if audio_sent:
                        # Resposta personalizada conectando com áudio + início do pitch de vendas
                        response = (
                            f"{extracted_name}, enviei um áudio especial do nosso comandante "
                            f"Hélio dos Anjos! Estamos na campanha de acesso à Série B e "
                            f"cada torcedor como você pode fazer a diferença.\n\n"
                            f"Torcedor, o Náutico precisa de você. Estamos no quadrangular "
                            f"pelo acesso à Série B. Seja sócio hoje e faça parte dessa volta histórica. "
                            f"Quer saber quais são os planos disponíveis ou já recebeu o link para garantir o seu?"
                        )
                    else:
                        # Se áudio não foi enviado, dar mensagem apropriada com pitch
                        response = (
                            f"Olá, {extracted_name}! Que bom te conhecer melhor. "
                            f"Estamos na campanha de acesso à Série B e é o momento perfeito "
                            f"para você apoiar o Náutico!\n\n"
                            f"Torcedor, o Náutico precisa de você. Estamos no quadrangular "
                            f"pelo acesso à Série B. Seja sócio hoje e faça parte dessa volta histórica. "
                            f"Quer saber quais são os planos disponíveis ou já recebeu o link para garantir o seu?"
                        )
                    
                    # Nota: A movimentação para "Em Qualificação" já foi feita no _handle_initial_trigger_audio
                    
                    return response, lead_info
                else:
                    # Nome não identificado ou inválido - tentar novamente
                    emoji_logger.system_warning(f"❓ Nome inválido detectado: '{message}' - solicitando novamente")
                    
                    # Mensagens variadas para diferentes situações
                    if len(message.strip()) < 3:
                        response = (
                            "Não entendi bem! Preciso do seu nome completo "
                            "para te atender direito. Pode me dizer seu nome e sobrenome?"
                        )
                    elif message.strip().lower() in ['eu', 'me', 'mim']:
                        response = (
                            "Sei que é você mesmo! Mas preciso saber como te chamar. "
                            "Qual é o seu nome? Me diga aí!"
                        )
                    else:
                        response = (
                            "Não consegui entender seu nome direito. "
                            "Pode me dizer seu nome completo? É para eu te tratar corretamente."
                        )
                    return response, lead_info

            # Etapa 2: Atualizar histórico e contexto do lead (APENAS para estados avançados)
            emoji_logger.system_debug("🔄 ATUALIZANDO CONTEXTO - Processando lead e histórico...")
            conversation_history, lead_info = await self._update_context(message, conversation_history, lead_info, execution_context.get("media"))
            emoji_logger.system_success(
                f"Contexto atualizado - Lead: {lead_info.get('name', 'N/A')}, "
                f"Histórico: {len(conversation_history)} msgs"
            )

            # Etapa 2.5: Verificar se lead está em Atendimento Humano
            emoji_logger.system_debug("👤 VERIFICAÇÃO HANDOFF - Verificando se IA deve ficar em silêncio...")
            if await self.stage_tools.check_human_handoff_status(lead_info):
                emoji_logger.system_info("🔇 SILÊNCIO ATIVADO - Lead em atendimento humano")
                return "<SILENCE>", lead_info
            emoji_logger.system_success("IA pode continuar - Lead não está em atendimento humano")

            # Etapa 2.7: Verificar e executar Etapa 0 (Gatilho Inicial - Áudio) - APENAS se necessário
            emoji_logger.system_debug("🎵 VERIFICAÇÃO ETAPA 0 - Verificando se deve enviar áudio inicial...")
            
            # IMPORTANTE: Só enviar áudio se o lead não passou ainda pelo processo inicial
            # Evita enviar áudio para conversas que já estão em andamento
            current_state = await self._get_conversation_state(lead_info)
            if current_state in ['name_collected'] and lead_info.get('current_stage') == 'INITIAL_CONTACT':
                emoji_logger.system_debug("🎵 Lead precisa receber áudio inicial...")
                await self._handle_initial_trigger_audio(lead_info, phone, conversation_history)
            else:
                emoji_logger.system_debug(f"🎵 Áudio inicial não necessário (estado: {current_state}, stage: {lead_info.get('current_stage')})")
            
            # Etapa 3: Sincronizar com serviços externos (CRM)
            emoji_logger.system_debug("🔗 SINCRONIZAÇÃO EXTERNA - Conectando com CRM...")
            lead_info = await self._sync_external_services(lead_info, phone)
            emoji_logger.system_success("Sincronização externa concluída")

            # Etapa 3.5: Sincronizar dados de tags e campos com o CRM
            emoji_logger.system_debug("🏷️ SINCRONIZAÇÃO CRM - Atualizando tags e campos...")
            await self._sync_crm_data(lead_info, conversation_history)
            emoji_logger.system_success("Dados CRM sincronizados")

            # Etapa 4: Gerar resposta via LLM (fluxo unificado)
            emoji_logger.system_debug("🧠 GERAÇÃO LLM - Processando resposta inteligente...")
            response = await self._generate_llm_response(message, lead_info, conversation_history, execution_context)
            emoji_logger.system_success(f"Resposta LLM gerada: '{response[:100]}...'")

            # Etapa 5: Finalizar e registrar a resposta
            # TEMPORARIAMENTE DESABILITADO: ConversationMonitor
            # emoji_logger.system_debug("Registrando resposta do assistente...")
            # await self.conversation_monitor.register_message(phone=phone, is_from_user=False, lead_info=lead_info)
            # emoji_logger.system_success("Resposta do assistente registrada")

            # Correção: Adicionar verificação do protocolo de silêncio ANTES de formatar
            if "<SILENCE>" in response or "<SILENCIO>" in response:
                emoji_logger.system_info(f"🔇 PROTOCOLO SILÊNCIO - Ativado para {phone}. Nenhuma mensagem será enviada.")
                return "<SILENCE>", lead_info

            final_response = response_formatter.ensure_response_tags(response)
            # ANÁLISE DA RESPOSTA PARA AÇÕES DO CRM
            await self._execute_crm_actions_from_response(final_response, lead_info, execution_context)
            
            # DEBUG FINAL: Estado do lead ao final do processamento
            emoji_logger.system_info(f"🔍 DEBUG FINAL: current_stage='{lead_info.get('current_stage')}', is_valid_payment={lead_info.get('is_valid_nautico_payment')}, payment_value={lead_info.get('payment_value')}")
            
            emoji_logger.agentic_success(
                f"✅ AGENTE STATELESS CONCLUÍDO - {phone}: "
                f"'{message[:50]}...' -> '{final_response[:50]}...'"
            )
            return final_response, lead_info

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            phone = execution_context.get("phone", "UNKNOWN")
            emoji_logger.system_error(
                "AgenticSDRStateless",
                f"❌ ERRO CRÍTICO NO AGENTE: {e}",
                traceback=error_trace
            )
            emoji_logger.agentic_error(
                f"💥 FALHA NO PROCESSAMENTO - {phone}: '{message[:50]}...' -> ERRO: {str(e)[:50]}..."
            )
            return (
                "Desculpe, tive um problema aqui. "
                "Pode repetir?",
                execution_context.get("lead_info", {})
            )

    async def _update_context(self, message: str, conversation_history: list, lead_info: dict, media_data: dict) -> tuple[list, dict]:
        """
        Prepara a mensagem do usuário, atualiza o histórico, enriquece as informações
        do lead e persiste as mudanças no banco de dados de forma atômica.
        """
        emoji_logger.system_debug("📝 PREPARAÇÃO MENSAGEM - Adicionando mensagem do usuário ao histórico...")
        
        # 1. Adicionar nova mensagem do usuário ao histórico
        user_message_content = [{"type": "text", "text": message}]
        if media_data:
            emoji_logger.system_debug("📎 PROCESSAMENTO MÍDIA - Detectada mídia na mensagem...")
            # (O restante do código de processamento de mídia permanece o mesmo)
            if media_data.get("type") == "error":
                raise ValueError(media_data.get("content", "Erro ao processar mídia."))
            media_content = media_data.get("content") or media_data.get("data", "")
            mime_type = media_data.get("mimetype", "application/octet-stream")
            if "base64," in media_content:
                media_content = media_content.split("base64,")[1]
            user_message_content.append({
                "type": "media",
                "media_data": {"mime_type": mime_type, "content": media_content}
            })
            emoji_logger.multimodal_event(f"📎 Mídia do tipo {mime_type} adicionada.")
            emoji_logger.system_info(f"🔍 INICIANDO PROCESSAMENTO MÍDIA: mime_type={mime_type}")
            media_result = await self.multimodal.process_media(media_data)
            emoji_logger.system_info(f"🔍 RESULTADO PROCESSAMENTO: success={media_result.get('success')}")
            if media_result.get("success"):
                analysis = media_result.get("analysis", {})
                
                # Processar comprovante de pagamento do Náutico
                extracted_payment_value = analysis.get("payment_value")
                if extracted_payment_value:
                    lead_info['membership_interest'] = 8  # Alto interesse por enviar comprovante
                    emoji_logger.system_info(f"Pagamento de R${extracted_payment_value} detectado - interesse alto definido.")
                
                # Debug: Verificar se chegou na análise de pagamento
                emoji_logger.system_info(f"🔍 ANÁLISE MÍDIA: analysis.keys()={list(analysis.keys()) if analysis else 'None'}")
                emoji_logger.system_info(f"🔍 IS_PAYMENT_RECEIPT: {analysis.get('is_payment_receipt') if analysis else 'No analysis'}")
                
                # Processar comprovante de pagamento do Náutico
                if analysis.get("is_payment_receipt"):
                    # VERIFICAÇÃO CRÍTICA: Evitar reprocessamento se pagamento já foi validado OU lead já qualificado
                    already_validated = lead_info.get('is_valid_nautico_payment', False)
                    current_stage = lead_info.get('current_stage', '').upper()
                    
                    # DEBUG: Verificar dados do lead
                    emoji_logger.system_info(f"🔍 DEBUG LEAD STATUS: already_validated={already_validated}, current_stage='{current_stage}', lead_id={lead_info.get('id')}")
                    
                    if already_validated or current_stage == 'QUALIFICADO':
                        emoji_logger.system_info(
                            "🔒 COMPROVANTE IGNORADO - Lead já validado/qualificado. "
                            f"Status: {current_stage}, Pagamento original: R${lead_info.get('payment_value', 'N/A')}"
                        )
                        # Não processar novamente, manter os dados existentes
                    else:
                        emoji_logger.system_info("🆕 PRIMEIRO COMPROVANTE - Processando validação de pagamento")
                        
                        payment_value = analysis.get("payment_value")
                        payer_name = analysis.get("payer_name")
                        is_valid_payment = analysis.get("is_valid_nautico_payment", False)
                        
                        # Armazenar informações do pagamento no lead_info
                        lead_info['payment_value'] = payment_value
                        lead_info['payer_name'] = payer_name
                        lead_info['is_valid_nautico_payment'] = is_valid_payment
                    
                    # Usar valores atuais (novos ou existentes)
                    current_payment_value = lead_info.get('payment_value')
                    current_payer_name = lead_info.get('payer_name')
                    current_is_valid = lead_info.get('is_valid_nautico_payment', False)
                    
                    emoji_logger.multimodal_event(
                        f"💰 Comprovante detectado - Valor: R${current_payment_value}, "
                        f"Pagador: {current_payer_name}, Válido: {current_is_valid}"
                    )
                    
                    # Debug adicional
                    emoji_logger.system_info(f"🔍 DEBUG: is_valid_payment={current_is_valid}, payment_value={current_payment_value}")
                    
                    # Se o comprovante é válido, qualificar automaticamente o lead (APENAS se ainda não foi qualificado)
                    emoji_logger.system_info(f"🔍 CONDIÇÃO QUALIFICAÇÃO: is_valid_payment={current_is_valid}, payment_value={current_payment_value}")
                    
                    # VERIFICAÇÃO ADICIONAL: Evitar requalificação se já está qualificado
                    current_stage = lead_info.get('current_stage', '').upper()
                    if current_stage == 'QUALIFICADO':
                        emoji_logger.system_info("🔒 LEAD JÁ QUALIFICADO - Ignorando nova tentativa de qualificação")
                    elif current_is_valid and current_payment_value and not already_validated:
                        emoji_logger.system_info("🎯 INICIANDO qualificação automática do lead")
                        try:
                            emoji_logger.system_info("🎯 Qualificando automaticamente lead com comprovante válido")
                            
                            # Mover para "Qualificado" usando a instância já inicializada com CRM service
                            qualification_result = await self.stage_tools.move_to_qualificado(
                                lead_info=lead_info,
                                payment_value=str(current_payment_value),
                                payment_valid=True,
                                notes=f"Qualificado automaticamente - Comprovante de pagamento válido de R${current_payment_value}"
                            )
                            
                            if qualification_result.get("success"):
                                emoji_logger.system_success(
                                    f"✅ Lead qualificado automaticamente - Pagamento R${current_payment_value} confirmado"
                                )
                                lead_info.update(qualification_result.get("updated_lead_info", {}))
                            else:
                                emoji_logger.system_error(
                                    f"Erro ao qualificar lead automaticamente: {qualification_result.get('message')}"
                                )
                                
                        except Exception as e:
                            emoji_logger.system_error(f"Erro na qualificação automática: {e}")
            else:
                emoji_logger.system_warning(f"Falha na extração de texto da mídia: {media_result.get('message')}")

        user_message = {"role": "user", "content": user_message_content, "timestamp": datetime.now().isoformat()}
        conversation_history.append(user_message)
        emoji_logger.system_success(f"Mensagem adicionada ao histórico. Total: {len(conversation_history)} mensagens")

        # 2. Analisar contexto da conversa para extração inteligente
        emoji_logger.system_debug("🔍 ANÁLISE CONTEXTUAL - Analisando contexto da conversa...")
        context = self.context_analyzer.analyze_context(conversation_history, lead_info)
        emoji_logger.system_success(
            f"Contexto analisado - Sentimento: {context.get('sentiment', 'N/A')}, "
            f"Urgência: {context.get('urgency_level', 'N/A')}"
        )
        
        # 3. Re-processar o histórico COMPLETO para obter o estado mais atual do lead
        # Agora com contexto para extração inteligente de nomes
        emoji_logger.system_debug("👤 EXTRAÇÃO LEAD - Re-processando histórico para extrair informações do lead...")
        updated_lead_info = self.lead_manager.extract_lead_info(
            conversation_history,
            existing_lead_info=lead_info,
            context=context
        )
        
        # CORREÇÃO: Preservar informações críticas de pagamento que podem ter sido perdidas
        # MAS APENAS se o lead ainda não foi qualificado (para evitar sobrescrever novos valores)
        current_stage = lead_info.get('current_stage', '').upper()
        
        if current_stage != 'QUALIFICADO':
            payment_fields = ['payment_value', 'payer_name', 'is_valid_nautico_payment']
            for field in payment_fields:
                if field in lead_info and field not in updated_lead_info:
                    updated_lead_info[field] = lead_info[field]
                    emoji_logger.system_info(f"🔒 PRESERVADO campo de pagamento: {field}={lead_info[field]}")
        else:
            emoji_logger.system_info("🔒 LEAD QUALIFICADO - Preservando valores originais, ignorando novos comprovantes")
        
        emoji_logger.system_success(
            f"Lead atualizado - Nome: '{updated_lead_info.get('name', 'N/A')}', "
            f"Valor: {updated_lead_info.get('payment_value', 'N/A')}"
        )

        # 4. Detectar e persistir mudanças no banco de dados
        emoji_logger.system_debug("🔄 DETECÇÃO MUDANÇAS - Verificando alterações no lead...")
        lead_changes = self._detect_lead_changes(lead_info, updated_lead_info)
        
        if lead_changes:
            lead_id_to_update = lead_info.get("id")
            if lead_id_to_update:
                try:
                    emoji_logger.system_info(f"Detectadas mudanças no lead {lead_id_to_update}. Sincronizando com o DB.", changes=lead_changes)
                    result = await supabase_client.update_lead(lead_id_to_update, lead_changes)
                    if result:
                        emoji_logger.system_success(f"Lead {lead_id_to_update} atualizado no Supabase.")
                    else:
                        emoji_logger.system_error("Lead Update", f"Falha ao atualizar lead {lead_id_to_update} no Supabase - resultado vazio.")
                except Exception as e:
                    emoji_logger.system_error("Lead Sync", f"Falha ao sincronizar mudanças do lead {lead_id_to_update} com o DB: {str(e)}")
                    # Continuar mesmo se a atualização falhar, para não interromper o fluxo.
            else:
                emoji_logger.system_debug("Lead sem ID - mudanças detectadas mas não persistidas")
        else:
            emoji_logger.system_debug("Nenhuma mudança detectada no lead")
        
        # 4. Retornar o histórico e o lead_info final e atualizado
        emoji_logger.system_success("✅ CONTEXTO ATUALIZADO - Histórico e lead_info finalizados")
        return conversation_history, updated_lead_info

    async def _sync_external_services(self, lead_info: dict, phone: str) -> dict:
        """
        MODIFICADO: Sincroniza leads existentes com Kommo após coleta de nome
        Não cria mais leads automaticamente - isso é feito no fluxo de estados
        """
        # Se não tem ID, significa que a criação é controlada pelo fluxo de estados
        # Não fazemos nada aqui
        if not lead_info.get("id"):
            emoji_logger.system_debug("Lead sem ID - criação controlada pelo fluxo de estados")
            return lead_info

        # CONDIÇÃO DE SINCRONIZAÇÃO: Lead já existe no Supabase, mas ainda não no Kommo
        elif lead_info.get("id") and lead_info.get("name") and not lead_info.get("kommo_lead_id"):
            emoji_logger.system_info(f"Lead {lead_info.get('id')} já existe no Supabase, tentando criar no Kommo.")
            try:
                kommo_response = await self.crm_service.create_lead(lead_info)
                if kommo_response.get("success"):
                    new_kommo_id = kommo_response.get("lead_id")
                    lead_info["kommo_lead_id"] = new_kommo_id
                    await supabase_client.update_lead(lead_info["id"], {"kommo_lead_id": new_kommo_id})
                    emoji_logger.team_crm(f"Lead existente sincronizado com Kommo. ID: {new_kommo_id}")
            except Exception as e:
                emoji_logger.system_error("Kommo Integration", f"Falha ao criar lead no Kommo para lead existente no Supabase: {str(e)}")

        return lead_info

    async def _execute_crm_actions_from_response(self, response: str, lead_info: dict, execution_context: dict):
        """Analisa a resposta da IA e executa ações do CRM conforme necessário"""
        try:
            response_text = response.lower()
            
            # VERIFICAÇÃO CRÍTICA: Não executar ações para leads já qualificados
            current_stage = lead_info.get('current_stage', '').upper()
            emoji_logger.system_info(f"🔍 DEBUG CRM ACTIONS: current_stage='{current_stage}', lead_id={lead_info.get('id')}")
            
            if current_stage == 'QUALIFICADO':
                emoji_logger.system_info("🔒 LEAD JÁ QUALIFICADO - Ignorando análise de CRM actions")
                return
            
            # Verificar se é confirmação de pagamento APENAS se já existe validação prévia de comprovante
            # IMPORTANTE: Só qualifica se já foi validado um comprovante anteriormente
            has_validated_payment = lead_info.get('is_valid_nautico_payment', False)
            payment_value = lead_info.get('payment_value')
            
            if has_validated_payment and payment_value:
                payment_indicators = [
                    "confirmado", "pagamento", "recebido", "bem-vindo ao sócio",
                    "sócio mais fiel", "r$", "valor", "confirmadíssimo"
                ]
                
                is_payment_confirmation = any(indicator in response_text for indicator in payment_indicators)
                has_value_mention = "r$" in response_text
                
                if is_payment_confirmation and has_value_mention:
                    emoji_logger.system_info("🎯 CONFIRMAÇÃO DE PAGAMENTO APÓS VALIDAÇÃO - Qualificando lead")
                    
                    # Qualificar lead usando a instância já inicializada com CRM service
                    result = await self.stage_tools.move_to_qualificado(
                        lead_info=lead_info,
                        payment_value=str(payment_value),
                        payment_valid=True,
                        notes=f"Qualificado após confirmação - Comprovante previamente validado de R${payment_value}"
                    )
                    
                    if result.get("success"):
                        emoji_logger.system_success("✅ Lead qualificado após confirmação de pagamento validado")
                        # Atualizar lead_info com dados atualizados
                        lead_info.update(result.get("updated_lead_info", {}))
                    else:
                        emoji_logger.system_error(f"Erro ao qualificar lead: {result.get('message')}")
            else:
                # Log para detectar tentativas de qualificação sem validação
                payment_indicators = [
                    "confirmado", "pagamento", "recebido", "bem-vindo ao sócio",
                    "sócio mais fiel", "confirmadíssimo"
                ]
                
                is_payment_confirmation = any(indicator in response_text for indicator in payment_indicators)
                
                if is_payment_confirmation:
                    emoji_logger.system_warning(
                        f"⚠️ TENTATIVA DE QUALIFICAÇÃO SEM COMPROVANTE VÁLIDO - "
                        f"has_validated_payment={has_validated_payment}, payment_value={payment_value}"
                    )
                    emoji_logger.system_info(
                        "🔒 QUALIFICAÇÃO BLOQUEADA - Lead só pode ser qualificado após envio e validação de comprovante"
                    )
                    
        except Exception as e:
            emoji_logger.system_error("CRM Actions", f"Erro ao executar ações do CRM: {e}")

    async def _sync_crm_data(self, lead_info: dict, conversation_history: list):
        """Gera e envia atualizações de campos e tags para o CRM."""
            
        kommo_lead_id = lead_info.get("kommo_lead_id")
        if not kommo_lead_id:
            emoji_logger.system_debug("CRM Sync: Pulando, lead sem kommo_lead_id.")
            return

        emoji_logger.system_debug(f"Gerando payload de atualização para lead {kommo_lead_id}...")
        update_payload = crm_sync_service.get_update_payload(
            lead_info=lead_info,
            conversation_history=conversation_history
        )

        if update_payload:
            try:
                emoji_logger.system_debug(f"Enviando atualização para Kommo: {update_payload}")
                await self.crm_service.update_lead(
                    lead_id=str(kommo_lead_id),
                    update_data=update_payload
                )
                emoji_logger.system_info("CRM Sync: Dados do lead atualizados no Kommo.", payload=update_payload)
            except Exception as e:
                emoji_logger.system_error("CRM Sync", f"Falha ao atualizar dados no Kommo: {str(e)}")
        else:
            emoji_logger.system_debug("Nenhuma atualização necessária para o CRM")

    

    async def _generate_llm_response(self, message: str, lead_info: dict, conversation_history: list, execution_context: dict) -> str:
        """Executa o fluxo normal de geração de resposta com o LLM."""
        context = {}  # Contexto pode ser enriquecido aqui se necessário
        return await self._generate_response(
            message=message,
            context=context,
            lead_info=lead_info,
            conversation_history=conversation_history,
            execution_context=execution_context
        )

    async def _execute_post_scheduling_workflow(
            self,
            schedule_result: dict,
            lead_info: dict,
            context: dict
    ):
        """
        Executa o workflow pós-agendamento de forma robusta.
        """
        kommo_lead_id = lead_info.get("kommo_lead_id")
        if not kommo_lead_id:
            emoji_logger.service_warning(
                "Kommo lead ID não encontrado. "
                "Pulando workflow pós-agendamento."
            )
            return

        emoji_logger.system_success(
            "✅ Workflow pós-agendamento executado com as devidas "
            "tratativas de erro."
        )

        # Agendar lembretes de reunião
        meeting_date_time = datetime.fromisoformat(schedule_result["start_time"])
        lead_email = lead_info.get("email")
        lead_name = lead_info.get("name", "")
        meet_link = schedule_result.get("meet_link", "")

        # Lembrete de 24 horas
        message_24h = (
            f"Oi {lead_name}! Tudo bem? Passando para confirmar sua reunião de amanhã às "
            f"{meeting_date_time.strftime('%H:%M')} para conhecer os planos do Náutico. Aqui está o link da reunião: "
            f"{meet_link} Está tudo certo para você?"
        )
        await self.followup_service.schedule_followup(
            phone_number=lead_info["phone_number"],
            message=message_24h,
            delay_hours=24,
            lead_info=lead_info
        )
        emoji_logger.followup_event(f"Lembrete de 24h agendado para {lead_name}.")

        # Lembrete de 2 horas
        message_2h = (
            f"{lead_name}, Sua reunião sobre o programa de sócios é daqui a 2 horas! Te esperamos às "
            f"{meeting_date_time.strftime('%H:%M')}! Link: {meet_link}"
        )
        await self.followup_service.schedule_followup(
            phone_number=lead_info["phone_number"],
            message=message_2h,
            delay_hours=2,
            lead_info=lead_info
        )
        emoji_logger.followup_event(f"Lembrete de 2h agendado para {lead_name}.")

    async def _parse_and_execute_tools(
            self,
            response: str,
            lead_info: dict,
            context: dict,
            conversation_history: list
    ) -> dict:
        """
        Parse e executa tool calls na resposta do agente.
        """
        emoji_logger.system_debug(f"Raw LLM response before tool parsing: {response}")
        tool_pattern = r'\[TOOL:\s*([^|\]]+?)\s*\|\s*([^\]]*)\]'
        tool_matches = []
        try:
            tool_matches = re.findall(tool_pattern, response)
        except re.error as e:
            emoji_logger.system_error(
                "Tool parsing error",
                f"Erro de regex ao parsear tools: {e}. Resposta: {response[:200]}..."
            )
            return {} # Retorna vazio se a regex falhar

        if not tool_matches:
            return {}

        tool_results = {}

        for match in tool_matches:
            service_method = match[0].strip()
            params_str = match[1].strip() if len(
                match) > 1 and match[1] else ""

            params = {}
            if params_str:
                param_pairs = params_str.split('|')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        params[key.strip()] = value.strip()

            try:
                result = await self._execute_single_tool(
                    service_method, params, lead_info, context, conversation_history
                )
                tool_results[service_method] = result
                emoji_logger.system_success(
                    f"✅ Tool executado: {service_method}"
                )
            except Exception as e:
                tool_results[service_method] = {"error": str(e)}
                emoji_logger.system_error(
                    "Tool execution error",
                    f"❌ Erro no tool {service_method}: {e}"
                )

        return tool_results

    async def _execute_single_tool(
            self,
            service_method: str,
            params: dict,
            lead_info: dict,
            context: dict,
            conversation_history: list
    ):
        """Executa um tool específico"""
        parts = service_method.split('.')
        if len(parts) != 2:
            raise ValueError(f"Formato inválido: {service_method}")

        service_name, method_name = parts

        if service_name == "calendar":
            if method_name == "check_availability":
                date_req = params.get("date_request", "")
                return await self.calendar_service.check_availability(
                    date_req
                )
            elif method_name == "schedule_meeting":
                # Garante que o nome do lead está atualizado antes de agendar
                updated_lead_info = self.lead_manager.extract_lead_info(
                    conversation_history,
                    existing_lead_info=lead_info,
                    context=context
                )
                lead_info.update(updated_lead_info)

                result = await self.calendar_service.schedule_meeting(
                    date=params.get("date"),
                    time=params.get("time"),
                    lead_info={
                        **lead_info,
                        "email": params.get("email", lead_info.get("email")),
                        "name": lead_info.get("name", "Cliente") # Fallback explícito
                    }
                )
                if result and result.get("success"):
                    # CRIA UM REGISTRO DE QUALIFICAÇÃO COM O ID DO EVENTO
                    event_id = result.get("google_event_id")
                    if event_id and lead_info.get("id"):
                        qualification_data = {
                            "lead_id": lead_info["id"],
                            "qualification_status": "QUALIFIED",
                            "google_event_id": event_id,
                            "meeting_scheduled_at": result.get("start_time"),
                            "notes": "Reunião agendada pelo agente de IA."
                        }
                        await supabase_client.create_lead_qualification(qualification_data)
                        emoji_logger.system_info(f"Registro de qualificação criado para o evento: {event_id}")

                    # ATUALIZA O ESTÁGIO DO LEAD PARA "REUNIÃO AGENDADA" NO CRM
                    if lead_info.get("kommo_lead_id"):
                        try:
                            await self.crm_service.update_lead_stage(
                                lead_id=str(lead_info["kommo_lead_id"]),
                                stage_name="reunião_agendada",
                                notes="Reunião agendada automaticamente pelo agente de IA",
                                phone_number=lead_info.get("phone_number")
                            )
                            emoji_logger.system_success(f"✅ Lead {lead_info['kommo_lead_id']} movido para estágio 'Reunião Agendada'")
                        except Exception as e:
                            emoji_logger.service_error(f"❌ Erro ao atualizar estágio do lead no CRM: {e}")
                            # Continua o fluxo mesmo se a atualização do CRM falhar

                    await self._execute_post_scheduling_workflow(
                        result,
                        lead_info,
                        context
                    )
                return result
            elif method_name == "suggest_times":
                return await self.calendar_service.suggest_times(lead_info)
            elif method_name == "cancel_meeting":
                latest_qualification = await supabase_client.get_latest_qualification(lead_info["id"])
                meeting_id = params.get("meeting_id") or (latest_qualification and latest_qualification.get("google_event_id"))
                
                if not meeting_id:
                    raise ValueError(
                        "ID da reunião não encontrado para cancelamento."
                    )
                return await self.calendar_service.cancel_meeting(meeting_id)
            elif method_name == "reschedule_meeting":
                return await self.calendar_service.reschedule_meeting(
                    date=params.get("date"),
                    time=params.get("time"),
                    lead_info=lead_info
                )

        elif service_name == "crm":
            if method_name == "update_stage":
                stage = params.get("stage", "").lower()
                phone_number = lead_info.get("phone_number")
                return await self.crm_service.update_lead_stage(
                    lead_id=lead_info.get("kommo_lead_id"),
                    stage_name=stage,
                    phone_number=phone_number
                )
            elif method_name == "update_field":
                field_name = params.get("field")
                field_value = params.get("value")
                if field_name and field_value:
                    return await self.crm_service.update_lead(
                        lead_info.get("kommo_lead_id"),
                        {"custom_fields_values": [{"field_id": self.crm_service.custom_fields.get(field_name), "values": [{"value": field_value}]}]}
                    )

        elif service_name == "followup":
            if method_name == "schedule":
                hours = int(params.get("hours", 24))
                message = params.get(
                    "message",
                    "Oi! Tudo bem? Ainda tem interesse em ser sócio do Náutico?"
                )
                return await self.followup_service.schedule_followup(
                    phone_number=lead_info.get("phone_number"),
                    message=message,
                    delay_hours=hours,
                    lead_info=lead_info
                )

        elif service_name == "knowledge":
            if method_name == "search":
                query = params.get("query")
                if not query:
                    raise ValueError("O parâmetro 'query' é obrigatório para a busca na base de conhecimento.")
                return await self.knowledge_service.search_knowledge_base(query)

        raise ValueError(f"Tool não reconhecido: {service_name}.{method_name}")

    async def _generate_response(
        self,
        message: str,
        context: dict,
        lead_info: dict,
        conversation_history: list,
        execution_context: dict,
        is_followup: bool = False
    ) -> str:
        """Gera a resposta do agente usando o ModelManager com injeção de contexto robusta."""
        import json

        # 1. Carrega o prompt do sistema (persona) e injeta o contexto de data/hora.
        system_prompt = "Você é um assistente de vendas." # Fallback inicial
        try:
            # Usar o prompt atualizado do Náutico
            with open("app/prompts/prompt-agente-nautico.atualizado.md", "r", encoding="utf-8") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            emoji_logger.system_warning("Arquivo de prompt atualizado não encontrado. Tentando prompt original.")
            try:
                with open("app/prompts/prompt-agente.md", "r", encoding="utf-8") as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                emoji_logger.system_warning("Nenhum arquivo de prompt encontrado. Usando fallback.")

        # Injeção de Contexto Temporal
        tz = pytz.timezone(settings.timezone)
        now = datetime.now(tz)
        current_date_str = now.strftime('%Y-%m-%d %H:%M')
        days_map = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
        day_of_week_pt = days_map[now.weekday()]
        
        date_context = f"<contexto_temporal>\nA data e hora atuais são: {current_date_str} ({day_of_week_pt}).\n</contexto_temporal>\n\n"
        
        # Injeção de Contexto de Validação de Pagamento
        payment_context = ""
        has_validated_payment = lead_info.get('is_valid_nautico_payment', False)
        payment_value = lead_info.get('payment_value')
        current_stage = lead_info.get('current_stage', '').upper()
        
        if has_validated_payment and payment_value:
            if current_stage == 'QUALIFICADO':
                payment_context = f"<contexto_pagamento>\nEste lead JÁ FOI QUALIFICADO com pagamento de R${payment_value}. Se enviarem novos comprovantes, apenas agradeça e confirme que o pagamento já foi processado. NÃO repita confirmações de boas-vindas.\n</contexto_pagamento>\n\n"
            else:
                payment_context = f"<contexto_pagamento>\nEste lead TEM comprovante de pagamento VALIDADO de R${payment_value}. Você PODE confirmar pagamento e dar boas-vindas.\n</contexto_pagamento>\n\n"
        else:
            payment_context = f"<contexto_pagamento>\nEste lead NÃO tem comprovante de pagamento validado. JAMAIS confirme pagamento sem receber e validar documento. Sempre solicite o comprovante antes de qualquer confirmação.\n</contexto_pagamento>\n\n"
        
        # Adicionar instrução crítica sobre formatação da resposta
        formatting_instruction = "\n\nIMPORTANTE: Responda sempre de forma direta, sem tags ou formatação especial. Use linguagem profissional e objetiva.\n"
        
        system_prompt_with_context = date_context + payment_context + system_prompt + formatting_instruction

        # 2. Prepara as mensagens para o modelo.
        if is_followup:
            # Para follow-ups, a 'message' é um prompt completo e contextual.
            messages_for_model = [{"role": "user", "content": message}]
        else:
            messages_for_model = list(conversation_history)

        # Limita o histórico para as últimas 200 mensagens para evitar sobrecarga de contexto
        if len(messages_for_model) > 200:
            emoji_logger.system_warning(
                "Histórico longo detectado, truncando para as últimas 200 mensagens.",
                original_size=len(messages_for_model)
            )
            messages_for_model = messages_for_model[-200:]

        # VERIFICAÇÃO CRÍTICA: Garantir que não estamos enviando conteúdo vazio.
        if not messages_for_model or not any(msg.get("content") for msg in messages_for_model):
            emoji_logger.model_error(
                f"Tentativa de chamar o modelo com conteúdo vazio. History len: {len(conversation_history)}, is_followup: {is_followup}"
            )
            return "Não consegui processar sua solicitação no momento."

        # 3. Primeira chamada ao modelo para obter a resposta inicial (que pode conter tools).
        response_text = await self.model_manager.get_response(
            messages=messages_for_model,
            system_prompt=system_prompt_with_context
        )

        if response_text:
            # 5. Analisa e executa ferramentas, se houver.
            tool_results = await self._parse_and_execute_tools(
                response_text, lead_info, context, conversation_history
            )
            if tool_results:
                # 6. Se ferramentas foram usadas, faz uma segunda chamada ao modelo com os resultados.
                tool_results_str = "\n".join(
                    [f"- {tool}: {result}" for tool, result in tool_results.items()]
                )

                final_instruction = (
                    f"""=== RESULTADO DAS FERRAMENTAS ===\nSua resposta inicial foi: \n'{response_text}'\nAs seguintes ferramentas foram executadas com estes resultados:\n{tool_results_str}\n\n=== INSTRUÇÃO FINAL ===\nCom base nos resultados das ferramentas, gere a resposta final, clara e amigável para o usuário. Siga TODAS as regras do seu prompt de sistema. Não inclua mais chamadas de ferramentas. Apenas a resposta final."""
                )

                # Adiciona a resposta do assistente (com tools) e a instrução final ao histórico
                messages_for_final_response = list(messages_for_model)
                messages_for_final_response.append({"role": "assistant", "content": response_text})
                messages_for_final_response.append({"role": "user", "content": final_instruction})

                response_text = await self.model_manager.get_response(
                    messages=messages_for_final_response,
                    system_prompt=system_prompt_with_context # Reutiliza o mesmo system_prompt com contexto
                )
                
                # CORREÇÃO DEFINITIVA: Validar resposta após execução de tools
                if not response_text:
                    emoji_logger.system_error(
                        "AgenticSDRStateless", 
                        "Segunda chamada ao LLM retornou None após execução de tools"
                    )
                    response_text = "As informações foram processadas com sucesso. Como posso ajudar mais?"
                elif re.search(r'\[\w+[:\.].*?\]', response_text):
                    emoji_logger.system_error(
                        "AgenticSDRStateless", 
                        f"Segunda chamada ao LLM ainda contém tools: {response_text[:100]}..."
                    )
                    response_text = "As informações foram processadas com sucesso. Como posso ajudar mais?"
                else:
                    emoji_logger.system_success(
                        f"Segunda chamada ao LLM bem-sucedida: {response_text[:50]}..."
                    )

        return response_text or "Não consegui gerar uma resposta no momento."

    def _detect_lead_changes(self, old_info: dict, new_info: dict) -> dict:
        """Detecta mudanças nas informações do lead."""
        changes = {}
        for key, value in new_info.items():
            if value and value != old_info.get(key):
                changes[key] = value
        return changes

    

    async def _sync_lead_changes(self, changes: dict, phone: str, lead_info: dict):
        """Sincroniza as mudanças do lead com o CRM."""
        if not self.crm_service.is_initialized:
            await self.crm_service.initialize()
            
        kommo_lead_id = lead_info.get("kommo_lead_id")
        if not kommo_lead_id:
            # Se não houver ID do Kommo, talvez criar um novo lead aqui
            return

        update_data = {}
        for key, value in changes.items():
            if key == "name":
                update_data["name"] = value
            elif key == "bill_value":
                update_data["bill_value"] = value
            elif key == "chosen_flow":
                update_data["chosen_flow"] = value
        
        if update_data:
            await self.crm_service.update_lead(kommo_lead_id, update_data)

    async def _handle_initial_trigger_audio(
        self,
        lead_info: Dict[str, Any],
        phone: str,
        conversation_history: list[dict]
    ) -> bool:
        """
        ETAPA 0: GATILHO INICIAL - Gerencia o envio do áudio do presidente
        MODIFICADO: Só envia áudio após coleta do nome conforme prompt atualizado
        """
        try:
            # NOVA VALIDAÇÃO: Só enviar se tem nome real coletado
            if not lead_info.get("name") or lead_info.get("name") == "Lead Náutico":
                emoji_logger.system_debug(
                    f"⏸️ Áudio bloqueado - aguardando coleta de nome para {phone}"
                )
                return False
            
            # Verificar se é uma conversa nova (critério: poucos mensagens no histórico)
            is_new_conversation = len(conversation_history) <= 2
            
            # Verificar se já enviou áudio inicial (evitar reenvio)
            already_sent_audio = lead_info.get("initial_audio_sent", False)
            
            # Verificar se lead está em estágio inicial
            current_stage = lead_info.get("current_stage", "").upper()
            is_initial_stage = current_stage in ["NOVO_LEAD", "INITIAL_CONTACT", "", "EM_QUALIFICACAO"]
            
            # DEBUG: Log detalhado das condições
            emoji_logger.system_debug(
                f"🔍 DEBUG ÁUDIO: {phone} - "
                f"is_new_conversation={is_new_conversation} (len={len(conversation_history)}), "
                f"already_sent_audio={already_sent_audio}, "
                f"current_stage='{current_stage}', is_initial_stage={is_initial_stage}"
            )
            
            # TEMPORÁRIO: Para novo lead com nome coletado, sempre tentar enviar áudio
            is_brand_new_lead = (
                lead_info.get("name") and 
                lead_info.get("name") != "Lead Náutico" and
                not already_sent_audio
            )
            
            should_send_audio = (
                is_brand_new_lead or 
                (is_new_conversation and not already_sent_audio and is_initial_stage)
            )
            
            emoji_logger.system_debug(
                f"🎵 DECISÃO ÁUDIO: should_send_audio={should_send_audio} "
                f"(brand_new={is_brand_new_lead}, new={is_new_conversation}, not_sent={not already_sent_audio}, initial={is_initial_stage})"
            )
            
            if should_send_audio:
                emoji_logger.system_info(
                    f"🎵 ETAPA 0 ATIVADA - Enviando áudio inicial do presidente para {phone}"
                )
                
                # Enviar áudio do presidente Hélio dos Anjos
                audio_result = await self.audio_service.send_initial_audio(
                    phone_number=phone,
                    lead_info=lead_info
                )
                
                if audio_result.get("success"):
                    emoji_logger.service_success(
                        f"✅ Áudio inicial enviado com sucesso para {phone}"
                    )
                    
                    # Marcar que o áudio foi enviado para evitar reenvios
                    lead_info["initial_audio_sent"] = True
                    
                    # Mover lead para "Em Qualificação" conforme prompt
                    stage_result = await self.stage_tools.move_to_em_qualificacao(
                        lead_info,
                        notes="Áudio inicial enviado - Laura iniciando qualificação"
                    )
                    
                    if stage_result.get("success"):
                        emoji_logger.service_success(
                            f"✅ Lead {lead_info.get('id')} movido para Em Qualificação"
                        )
                    
                    # Agendar follow-ups automáticos do Náutico
                    followup_result = await self.followup_nautico_tools.schedule_nautico_followups(
                        lead_info, phone
                    )
                    
                    if followup_result.get("success"):
                        emoji_logger.followup_event(
                            f"✅ {followup_result.get('total', 0)} follow-ups agendados para {phone}"
                        )
                    
                    # Atualizar lead info no Supabase com flag de áudio enviado
                    try:
                        lead_id = lead_info.get("id")
                        if lead_id:
                            await supabase_client.update_lead(lead_id, {
                                "initial_audio_sent": True
                            })
                    except Exception as e:
                        emoji_logger.system_warning(
                            f"Erro ao atualizar flag de áudio no Supabase: {e}"
                        )
                    
                    return True  # Áudio enviado com sucesso
                else:
                    emoji_logger.service_error(
                        f"❌ Falha ao enviar áudio inicial: {audio_result.get('message')}"
                    )
                    return False  # Falha ao enviar áudio
            else:
                # Log do motivo por não enviar
                reasons = []
                if not is_new_conversation:
                    reasons.append("conversa não é nova")
                if already_sent_audio:
                    reasons.append("áudio já foi enviado")
                if not is_initial_stage:
                    reasons.append(f"estágio não é inicial ({current_stage})")
                    
                emoji_logger.system_debug(
                    f"🎵 Áudio inicial não enviado para {phone} - Motivos: {', '.join(reasons)}"
                )
                return False  # Áudio não foi enviado
                
        except Exception as e:
            emoji_logger.system_error(
                "AgenticSDRStateless",
                f"Erro na Etapa 0 (áudio inicial): {e}"
            )
            return False  # Erro na execução

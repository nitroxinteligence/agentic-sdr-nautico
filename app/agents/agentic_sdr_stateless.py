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
        calendar_real = CalendarServiceReal() if not settings.disable_google_calendar else None
        crm_real = CRMServiceReal() if settings.enable_crm_integration else None
        followup_real = FollowUpServiceReal() if settings.enable_follow_up_automation else None
        knowledge_real = KnowledgeService() if settings.enable_knowledge_base else None
        
        # Aplicar wrappers condicionais
        self.calendar_service = CalendarServiceWrapper(calendar_real) if calendar_real else None
        self.crm_service = CRMServiceWrapper(crm_real) if crm_real else None
        self.followup_service = FollowUpServiceWrapper(followup_real) if followup_real else None
        self.knowledge_service = KnowledgeServiceWrapper(knowledge_real) if knowledge_real else None

        self.is_initialized = False

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
            await self.conversation_monitor.initialize()
            
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
                f"AgenticSDRStateless - Erro na inicialização: {e}"
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

            emoji_logger.system_debug("Registrando mensagem do usuário...")
            await self.conversation_monitor.register_message(phone=phone, is_from_user=True, lead_info=lead_info)
            emoji_logger.system_success("Mensagem do usuário registrada")

            # Etapa 2: Atualizar histórico e contexto do lead
            emoji_logger.system_debug("🔄 ATUALIZANDO CONTEXTO - Processando lead e histórico...")
            conversation_history, lead_info = await self._update_context(message, conversation_history, lead_info, execution_context.get("media"))
            emoji_logger.system_success(
                f"Contexto atualizado - Lead: {lead_info.get('name', 'N/A')}, "
                f"Histórico: {len(conversation_history)} msgs"
            )

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
            emoji_logger.system_debug("Registrando resposta do assistente...")
            await self.conversation_monitor.register_message(phone=phone, is_from_user=False, lead_info=lead_info)
            emoji_logger.system_success("Resposta do assistente registrada")

            # Correção: Adicionar verificação do protocolo de silêncio ANTES de formatar
            if "<SILENCE>" in response or "<SILENCIO>" in response:
                emoji_logger.system_info(f"🔇 PROTOCOLO SILÊNCIO - Ativado para {phone}. Nenhuma mensagem será enviada.")
                return "<SILENCE>", lead_info

            final_response = response_formatter.ensure_response_tags(response)
            emoji_logger.agentic_success(
                f"✅ AGENTE STATELESS CONCLUÍDO - {phone}: "
                f"'{message[:50]}...' -> '{final_response[:50]}...'"
            )
            return final_response, lead_info

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            emoji_logger.system_error(
                f"AgenticSDRStateless - ❌ ERRO CRÍTICO NO AGENTE: {e}",
                traceback=error_trace
            )
            emoji_logger.agentic_error(
                f"💥 FALHA NO PROCESSAMENTO - {phone}: '{message[:50]}...' -> ERRO: {str(e)[:50]}..."
            )
            return (
                "<RESPOSTA_FINAL>Desculpe, tive um problema aqui. "
                "Pode repetir?</RESPOSTA_FINAL>",
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
            media_result = await self.multimodal.process_media(media_data)
            if media_result.get("success"):
                extracted_bill_value = media_result.get("analysis", {}).get("bill_value")
                if extracted_bill_value:
                    lead_info['bill_value'] = extracted_bill_value
                    emoji_logger.system_info(f"Valor da conta R${extracted_bill_value} extraído e injetado no lead_info.")
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
        emoji_logger.system_success(
            f"Lead atualizado - Nome: '{updated_lead_info.get('name', 'N/A')}', "
            f"Valor: {updated_lead_info.get('bill_value', 'N/A')}"
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
        Cria e sincroniza informações do lead com Supabase e Kommo.
        A criação ocorre quando o lead ainda não tem um ID do Supabase, garantindo
        captura de todos os contatos desde a primeira interação.
        """
        # Supabase é sempre necessário para operações de lead
            
        # CONDIÇÃO DE CRIAÇÃO: Lead ainda não foi salvo no banco (sem 'id')
        # Removida exigência de nome para capturar todos os contatos desde primeira interação
        if not lead_info.get("id"):
            emoji_logger.system_info(f"Iniciando criação de novo lead para {phone} com nome '{lead_info.get('name')}'.")
            try:
                # 1. Criar no Supabase para obter um ID estável
                lead_data_to_create = {**lead_info, "phone_number": phone}
                created_supabase_lead = await supabase_client.create_lead(lead_data_to_create)
                
                if not created_supabase_lead or not created_supabase_lead.get("id"):
                    emoji_logger.system_error("Lead Creation", "Falha crítica: Supabase não retornou um lead válido após a criação.")
                    return lead_info # Retorna o lead_info original sem ID

                lead_info.update(created_supabase_lead)
                emoji_logger.supabase_insert("leads", 1, phone=phone, name=lead_info.get("name"), lead_id=lead_info.get("id"))

                # 2. Criar no Kommo, agora que temos um ID do Supabase
                try:
                    emoji_logger.system_info(f"Tentando criar lead no Kommo para o lead_id {lead_info.get('id')}.")
                    kommo_response = await self.crm_service.create_lead(lead_info)
                    if kommo_response.get("success"):
                        new_kommo_id = kommo_response.get("lead_id")
                        lead_info["kommo_lead_id"] = new_kommo_id
                        
                        # 3. Atualizar o lead do Supabase com o ID do Kommo
                        await supabase_client.update_lead(lead_info["id"], {"kommo_lead_id": new_kommo_id})
                        emoji_logger.team_crm(f"Lead criado no Kommo com ID: {new_kommo_id} e sincronizado com Supabase.")
                    else:
                        emoji_logger.system_warning("Não foi possível criar o lead no Kommo, mas o lead do Supabase foi criado.", lead_id=lead_info.get("id"))
                except Exception as crm_error:
                    emoji_logger.system_debug(f"CRM não disponível ou erro na criação: {str(crm_error)}")

            except Exception as e:
                emoji_logger.system_error("Lead Creation", f"Falha na criação e sincronização inicial do lead: {str(e)}", traceback_info=traceback.format_exc())
                # Retorna o lead_info original para não quebrar o fluxo principal
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
            f"{meeting_date_time.strftime('%H:%M')} com o Leonardo. Aqui está o link da reunião: "
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
            f"{lead_name}, Sua reunião com o Leonardo é daqui a 2 horas! Te esperamos às "
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
                f"Tool parsing error - Erro de regex ao parsear tools: {e}. Resposta: {response[:200]}..."
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
                    f"Tool execution error - ❌ Erro no tool {service_method}: {e}"
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
                    "Oi! Tudo bem? Ainda tem interesse em energia solar?"
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
            with open("app/prompts/prompt-agente.md", "r", encoding="utf-8") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            emoji_logger.system_warning("Arquivo de prompt principal não encontrado. Usando fallback.")

        # Injeção de Contexto Temporal
        tz = pytz.timezone(settings.timezone)
        now = datetime.now(tz)
        current_date_str = now.strftime('%Y-%m-%d %H:%M')
        days_map = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
        day_of_week_pt = days_map[now.weekday()]
        
        date_context = f"<contexto_temporal>\nA data e hora atuais são: {current_date_str} ({day_of_week_pt}).\n</contexto_temporal>\n\n"
        system_prompt_with_context = date_context + system_prompt

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
            return "<RESPOSTA_FINAL>Não consegui processar sua solicitação no momento.</RESPOSTA_FINAL>"

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

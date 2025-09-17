"""
Cliente Supabase para o SDR IA Náutico
Gerencia todas as operações com o banco de dados
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from supabase import create_client, Client
from loguru import logger
from app.utils.logger import emoji_logger
from app.utils.retry_decorator import supabase_retry, supabase_safe_operation

from app.config import settings


class SupabaseClient:
    """Cliente para interação com Supabase"""

    def __init__(self):
        """Inicializa o cliente Supabase"""
        # Usar supabase_key ou supabase_service_key dependendo da disponibilidade
        supabase_key = settings.supabase_key or settings.supabase_service_key

        if not settings.supabase_url:
            raise Exception("supabase_url is required")
        if not supabase_key:
            raise Exception("supabase_key is required")

        original_client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=supabase_key
        )

        # Criar wrapper do cliente que intercepta TODAS as operações
        self.client = self._create_intercepted_client(original_client)

    def _create_intercepted_client(self, original_client):
        """Cria um wrapper do cliente que intercepta operações da tabela leads"""

        class InterceptedClient:
            def __init__(self, original):
                self._original = original
                # Copiar todos os atributos e métodos do cliente original
                for attr in dir(original):
                    if not attr.startswith('_') and attr != 'table':
                        setattr(self, attr, getattr(original, attr))

            def table(self, table_name: str):
                """Intercepta chamadas para a tabela"""
                if table_name == "leads":
                    return self._get_intercepted_leads_table()
                else:
                    return self._original.table(table_name)

            def _get_intercepted_leads_table(self):
                """Retorna tabela leads com interceptação ultra rigorosa"""
                original_table = self._original.table("leads")

                class InterceptedLeadsTable:
                    def __init__(self, original):
                        self._original = original
                        # Copiar métodos não interceptados
                        for attr in dir(original):
                            if not attr.startswith('_') and attr not in ['insert']:
                                setattr(self, attr, getattr(original, attr))

                    def insert(self, data):
                        """Interceptação ULTRA rigorosa de inserções"""
                        import traceback

                        emoji_logger.system_error(f"🚨 ULTRA INTERCEPTED: Tentativa de inserir na tabela leads: {data}")
                        emoji_logger.system_error(f"🚨 STACK TRACE: {traceback.format_stack()}")

                        # Verificar se há phone_number com unknown
                        if isinstance(data, dict):
                            phone = str(data.get('phone_number', ''))
                            if 'unknown' in phone.lower():
                                emoji_logger.system_error(f"🚫 ULTRA BLOCKED: Inserção unknown_* TOTALMENTE BLOQUEADA: {phone}")
                                # Retornar fake result
                                return type('FakeResult', (), {'data': [{"id": "blocked", **data}]})()

                        emoji_logger.system_error(f"✅ ULTRA PERMITTED: Inserção permitida: {data}")
                        return self._original.insert(data)

                return InterceptedLeadsTable(original_table)

        return InterceptedClient(original_client)


    async def test_connection(self) -> bool:
        """Testa conexão com o Supabase"""
        try:
            self.client.table('leads').select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Erro de conexão Supabase: {str(e)}")
            return False

    # ============= LEADS =============

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo lead com retry automático"""

        # VALIDAÇÃO ULTRA CRÍTICA: Qualquer phone_number que comece com "unknown" é REJEITADO
        phone_number = str(lead_data.get('phone_number', ''))

        emoji_logger.system_error(f"🔍 ULTRA DEBUG CREATE_LEAD: phone_number='{phone_number}', lead_data={lead_data}")

        if 'unknown' in phone_number.lower():
            import traceback
            stack_trace = traceback.format_stack()
            emoji_logger.system_error(f"🚫 ULTRA BLOQUEIO: Rejeitando lead com phone_number contendo 'unknown': {phone_number}")
            emoji_logger.system_error(f"🔍 STACK TRACE: {stack_trace}")

            # RETORNAR LEAD FAKE ao invés de criar um inválido
            fake_lead = {
                "id": "00000000-0000-0000-0000-000000000000",
                "phone_number": phone_number,
                "name": lead_data.get("name", ""),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            emoji_logger.system_error(f"🔄 RETORNANDO LEAD FAKE para evitar criação inválida: {fake_lead}")
            return fake_lead

        # Validação adicional: phone_number deve ter pelo menos 10 dígitos
        digits_only = ''.join(filter(str.isdigit, phone_number))
        if len(digits_only) < 10:
            emoji_logger.system_error(f"🚫 BLOQUEADO: phone_number muito curto: {phone_number} (dígitos: {digits_only})")
            raise ValueError(f"Phone number inválido: {phone_number}")

        lead_data['created_at'] = datetime.now().isoformat()
        lead_data['updated_at'] = datetime.now().isoformat()

        result = self.client.table('leads').insert(lead_data).execute()

        if result.data:
            return result.data[0]

        raise Exception("Erro ao criar lead")

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def get_lead_by_phone(
            self, phone: str
    ) -> Optional[Dict[str, Any]]:
        """Busca lead por telefone com retry automático"""
        result = self.client.table('leads').select("*").eq(
            'phone_number', phone
        ).execute()

        if result.data:
            return result.data[0]

        return None

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def update_lead(
            self, lead_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza dados do lead com retry automático"""
        update_data['updated_at'] = datetime.now().isoformat()

        result = self.client.table('leads').update(update_data).eq(
            'id', lead_id
        ).execute()

        if result.data:
            return result.data[0]

        raise Exception("Erro ao atualizar lead")

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def delete_lead(self, lead_id: str) -> bool:
        """Deleta um lead do banco de dados"""
        try:
            result = self.client.table('leads').delete().eq('id', lead_id).execute()
            return True
        except Exception as e:
            emoji_logger.system_error(f"Erro ao deletar lead {lead_id}: {e}")
            raise

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def delete_messages_by_lead(self, lead_id: str) -> bool:
        """Deleta todas as mensagens de um lead"""
        try:
            result = self.client.table('messages').delete().eq('lead_id', lead_id).execute()
            return True
        except Exception as e:
            emoji_logger.system_error(f"Erro ao deletar mensagens do lead {lead_id}: {e}")
            raise

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def delete_conversation_by_phone(self, phone: str) -> bool:
        """Deleta conversa por telefone"""
        try:
            result = self.client.table('conversations').delete().eq('phone_number', phone).execute()
            return True
        except Exception as e:
            emoji_logger.system_error(f"Erro ao deletar conversa para {phone}: {e}")
            raise

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def delete_follow_ups_by_lead(self, lead_id: str) -> bool:
        """Deleta todos os follow-ups de um lead"""
        try:
            result = self.client.table('follow_ups').delete().eq('lead_id', lead_id).execute()
            return True
        except Exception as e:
            emoji_logger.system_error(f"Erro ao deletar follow-ups do lead {lead_id}: {e}")
            raise

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def delete_qualifications_by_lead(self, lead_id: str) -> bool:
        """Deleta todas as qualificações de um lead"""
        try:
            result = self.client.table('leads_qualifications').delete().eq('lead_id', lead_id).execute()
            return True
        except Exception as e:
            emoji_logger.system_error(f"Erro ao deletar qualificações do lead {lead_id}: {e}")
            raise

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def delete_analytics_by_phone(self, phone: str) -> bool:
        """Deleta eventos de analytics por telefone"""
        try:
            # Analytics pode ter phone_number ou nos dados do evento
            result = self.client.table('analytics').delete().or_(
                f'phone_number.eq.{phone},event_data->>phone_number.eq.{phone}'
            ).execute()
            return True
        except Exception as e:
            emoji_logger.system_error(f"Erro ao deletar analytics para {phone}: {e}")
            # Não fazer raise para analytics, pois pode não existir a coluna
            return False

    async def get_qualified_leads(self) -> List[Dict[str, Any]]:
        """Retorna leads qualificados"""
        try:
            result = self.client.table('leads').select("*").eq(
                'qualification_status', 'QUALIFIED'
            ).execute()

            return result.data or []

        except Exception as e:
            emoji_logger.supabase_error(
                f"Erro ao buscar leads qualificados: {str(e)}", table="leads"
            )
            return []
    
    async def search_leads_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Busca leads por nome (busca parcial, case-insensitive)"""
        try:
            # Busca leads com nome similar (case-insensitive)
            result = self.client.table('leads').select(
                "id, name, phone_number, created_at"
            ).ilike('name', f'%{name}%').order(
                'created_at', desc=True
            ).limit(5).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Erro ao buscar leads por nome '{name}': {str(e)}")
            return []

    # ============= CONVERSATIONS =============

    async def get_or_create_conversation(
            self, phone: str, lead_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Busca ou cria uma conversa para o telefone"""
        try:
            conversation = await self.get_conversation_by_phone(phone)

            if conversation:
                return conversation

            return await self.create_conversation(phone, lead_id)

        except Exception as e:
            emoji_logger.supabase_error(
                f"Erro ao obter/criar conversa: {str(e)}",
                table="conversations"
            )
            raise

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def create_conversation(
            self, phone: str, lead_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria uma nova conversa com retry automático"""
        session_id = f"session_{uuid4().hex}"

        conversation_data = {
            'phone_number': phone,
            'lead_id': lead_id,
            'session_id': session_id,
            'status': 'ACTIVE',
            'is_active': True,
            'total_messages': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        result = self.client.table('conversations').insert(
            conversation_data
        ).execute()

        if result.data:
            return result.data[0]

        raise Exception("Erro ao criar conversa")

    @supabase_safe_operation(default_return=None)
    async def get_conversation_by_phone(
            self, phone: str
    ) -> Optional[Dict[str, Any]]:
        """Busca dados da conversa por número de telefone com retry automático"""
        lead_result = self.client.table('leads').select('id').eq(
            'phone_number', phone
        ).execute()

        if not lead_result.data:
            return None

        lead_id = lead_result.data[0]['id']

        conversation_result = self.client.table('conversations').select(
            'id, emotional_state, current_stage, created_at, updated_at'
        ).eq('lead_id', lead_id).execute()

        if conversation_result.data:
            return conversation_result.data[0]

        return None

    async def get_conversation_emotional_state(
            self, conversation_id: str
    ) -> str:
        """Obtém estado emocional atual da conversa"""
        try:
            result = self.client.table('conversations').select(
                'emotional_state'
            ).eq('id', conversation_id).execute()

            if result.data:
                return result.data[0].get('emotional_state', 'neutro')

            return 'neutro'

        except Exception as e:
            logger.error(f"Erro ao obter estado emocional: {str(e)}")
            return 'neutro'

    async def update_conversation_emotional_state(
            self, conversation_id: str, emotional_state: str
    ) -> None:
        """Atualiza o estado emocional da conversa com validação"""
        try:
            valid_states = [
                'ENTUSIASMADA', 'CURIOSA', 'CONFIANTE', 'DUVIDOSA', 'NEUTRA'
            ]

            if emotional_state not in valid_states:
                emoji_logger.system_warning(
                    f"Estado emocional inválido: {emotional_state}, "
                    f"usando NEUTRA como fallback"
                )
                emotional_state = 'NEUTRA'

            await self.update_conversation(
                conversation_id,
                {'emotional_state': emotional_state}
            )
            emoji_logger.system_debug(
                f"Estado emocional atualizado para: {emotional_state}"
            )
        except Exception as e:
            emoji_logger.supabase_error(
                f"Erro ao atualizar estado emocional: {str(e)}",
                table="conversations"
            )

    # ============= MESSAGES =============

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def save_message(
            self, message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Salva mensagem no banco com retry automático"""
        message_data['created_at'] = datetime.now().isoformat()

        result = self.client.table('messages').insert(
            message_data
        ).execute()

        if result.data:
            if message_data.get('conversation_id'):
                await self._increment_message_count(
                    message_data['conversation_id']
                )

            return result.data[0]

        raise Exception("Erro ao salvar mensagem")

    @supabase_safe_operation(default_return=[])
    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """Retorna mensagens de uma conversa com contexto expandido"""
        result = self.client.table('messages').select("*").eq(
            'conversation_id', conversation_id
        ).order('created_at', desc=True).limit(limit).execute()

        if result.data:
            result.data.reverse()

        return result.data or []

    async def _increment_message_count(self, conversation_id: str):
        """Incrementa contador de mensagens na conversa"""
        try:
            conv = self.client.table('conversations').select(
                "total_messages"
            ).eq('id', conversation_id).execute()

            if conv.data:
                current_count = conv.data[0].get('total_messages', 0)

                self.client.table('conversations').update({
                    'total_messages': current_count + 1,
                    'updated_at': datetime.now().isoformat()
                }).eq('id', conversation_id).execute()

        except Exception as e:
            logger.error(f"Erro ao incrementar contador: {str(e)}")

    # ============= FOLLOW-UPS =============

    @supabase_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
    async def create_follow_up(
            self, follow_up_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria um follow-up com retry automático"""
        follow_up_data['created_at'] = datetime.now().isoformat()
        follow_up_data['updated_at'] = datetime.now().isoformat()

        result = self.client.table('follow_ups').insert(
            follow_up_data
        ).execute()

        if result.data:
            logger.info(f"Follow-up criado: {result.data[0]['id']}")
            return result.data[0]

        raise Exception("Erro ao criar follow-up")

    async def get_pending_follow_ups(self) -> List[Dict[str, Any]]:
        """Retorna follow-ups pendentes"""
        try:
            # Usar UTC para consistência com a criação de follow-ups
            from datetime import timezone
            now = datetime.now(timezone.utc).isoformat()

            result = self.client.table('follow_ups').select("*").eq(
                'status', 'pending'
            ).lte('scheduled_at', now).order('priority', desc=True).execute()

            follow_ups = result.data or []
            if follow_ups:
                logger.info(f"🔍 FOLLOW-UPS PENDENTES: {len(follow_ups)} encontrados. Tempo atual: {now}")
                for i, fu in enumerate(follow_ups[:3]):  # Log dos primeiros 3
                    scheduled_at = fu.get('scheduled_at', 'N/A')
                    fu_type = fu.get('follow_up_type', 'N/A') 
                    lead_id = fu.get('lead_id', 'N/A')
                    logger.info(f"    Follow-up {i+1}: Lead={lead_id[:8] if lead_id else 'N/A'}..., Tipo={fu_type}, Agendado={scheduled_at}")
            
            return follow_ups

        except Exception as e:
            logger.error(f"Erro ao buscar follow-ups: {str(e)}")
            return []

    async def update_follow_up_status(
        self,
        follow_up_id: str,
        status: str,
        executed_at: Optional[datetime] = None,
        reason: str = None
    ) -> Dict[str, Any]:
        """Atualiza status do follow-up"""
        logger.debug(f"Attempting to update follow-up {follow_up_id} to status '{status}' with data: {executed_at}")
        
        update_data = {
            'status': status,
            'updated_at': datetime.now().isoformat()
        }

        if executed_at:
            update_data['executed_at'] = executed_at.isoformat()
            
        if reason:
            update_data['error_reason'] = reason

        try:
            result = self.client.table('follow_ups').update(update_data).eq(
                'id', follow_up_id
            ).execute()

            if result.data:
                return result.data[0]

            raise Exception("Erro ao atualizar follow-up")

        except Exception as e:
            logger.error(f"Erro ao atualizar follow-up {follow_up_id} with data {update_data}: {str(e)}")
            raise

    # ============= KNOWLEDGE BASE =============

    async def add_knowledge(
            self, knowledge_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adiciona item à base de conhecimento"""
        try:
            knowledge_data['created_at'] = datetime.now().isoformat()
            knowledge_data['updated_at'] = datetime.now().isoformat()

            result = self.client.table('knowledge_base').insert(
                knowledge_data
            ).execute()

            if result.data:
                logger.info(
                    f"Conhecimento adicionado: {result.data[0]['id']}"
                )
                return result.data[0]

            raise Exception("Erro ao adicionar conhecimento")

        except Exception as e:
            logger.error(f"Erro ao adicionar conhecimento: {str(e)}")
            raise

    # ============= ANALYTICS =============

    async def log_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra evento de analytics"""
        try:
            event_data['timestamp'] = datetime.now().isoformat()
            event_data['created_at'] = datetime.now().isoformat()

            result = self.client.table('analytics').insert(
                event_data
            ).execute()

            if result.data:
                return result.data[0]

            raise Exception("Erro ao registrar evento")

        except Exception as e:
            logger.error(f"Erro ao registrar evento: {str(e)}")
            raise

    async def get_daily_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do dia"""
        try:
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0
            ).isoformat()

            leads = self.client.table('leads').select(
                "id", count='exact'
            ).gte('created_at', today_start).execute()

            qualified = self.client.table('leads').select(
                "id", count='exact'
            ).gte('created_at', today_start).eq(
                'qualification_status', 'QUALIFIED'
            ).execute()

            active_convs = self.client.table('conversations').select(
                "id", count='exact'
            ).eq('status', 'ACTIVE').execute()

            meetings = self.client.table('leads_qualifications').select(
                "id", count='exact'
            ).gte('meeting_scheduled_at', today_start).execute()

            return {
                'date': datetime.now().date().isoformat(),
                'total_leads': leads.count if leads else 0,
                'qualified_leads': qualified.count if qualified else 0,
                'active_conversations': (
                    active_convs.count if active_convs else 0
                ),
                'meetings_scheduled': meetings.count if meetings else 0
            }

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {
                'date': datetime.now().date().isoformat(),
                'total_leads': 0,
                'qualified_leads': 0,
                'active_conversations': 0,
                'meetings_scheduled': 0
            }

    # ============= LEAD QUALIFICATIONS =============

    async def create_lead_qualification(
            self, qualification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria uma qualificação de lead"""
        try:
            if 'qualification_status' not in qualification_data:
                qualification_data['qualification_status'] = 'QUALIFIED'

            if 'score' not in qualification_data:
                qualification_data['score'] = 80

            if 'criteria' not in qualification_data:
                qualification_data['criteria'] = {
                    'meeting_scheduled': True,
                    'interest_level': 'high',
                    'decision_maker': True
                }

            if 'notes' not in qualification_data:
                qualification_data['notes'] = (
                    'Lead qualificado - Reunião agendada com sucesso'
                )

            qualification_data['qualified_at'] = datetime.now().isoformat()
            qualification_data['created_at'] = datetime.now().isoformat()
            qualification_data['updated_at'] = datetime.now().isoformat()

            result = self.client.table('leads_qualifications').insert(
                qualification_data
            ).execute()

            if result.data:
                logger.info(
                    f"✅ Qualificação criada para lead "
                    f"{qualification_data['lead_id']}"
                )
                return result.data[0]

            raise Exception("Erro ao criar qualificação")

        except Exception as e:
            logger.error(f"Erro ao criar qualificação: {str(e)}")
            raise

    async def close(self):
        """Fecha conexão com Supabase"""
        pass

    async def save_qualification(
            self, qualification_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Salva resultado de qualificação"""
        try:
            qualification_data['created_at'] = datetime.now().isoformat()
            qualification_data['updated_at'] = datetime.now().isoformat()

            result = self.client.table('leads_qualifications').insert(
                qualification_data
            ).execute()

            if result.data:
                logger.info(
                    f"✅ Qualificação salva para lead "
                    f"{qualification_data['lead_id']}"
                )
                return result.data[0]

            raise Exception("Erro ao salvar qualificação")

        except Exception as e:
            logger.error(f"Erro ao salvar qualificação: {str(e)}")
            raise

    async def get_latest_qualification(
            self, lead_id: str
    ) -> Optional[Dict[str, Any]]:
        """Obtém última qualificação do lead"""
        try:
            response = self.client.table("leads_qualifications").select(
                "*"
            ).eq("lead_id", lead_id).order(
                "created_at", desc=True
            ).limit(1).execute()

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logger.error(f"Erro ao obter qualificação: {e}")
            return None

    @supabase_safe_operation(default_return=None)
    async def get_lead_by_id(
            self, lead_id: str
    ) -> Optional[Dict[str, Any]]:
        """Busca lead por ID com tratamento de erro automático"""
        response = self.client.table("leads").select("*").eq(
            "id", lead_id
        ).execute()

        if response.data:
            return response.data[0]
        return None

    async def get_recent_followup_count(
            self, lead_id: str, since: datetime
    ) -> int:
        """
        Conta o número de follow-ups realmente EXECUTADOS (não apenas criados)
        para um lead recentemente, baseado em quando foram executados, não criados.
        """
        try:
            # Contar apenas follow-ups que foram realmente executados (status executed ou failed)
            attempt_statuses = ['executed', 'failed']

            result = await asyncio.to_thread(
                self.client.table('follow_ups').select(
                    'id', count='exact'
                ).eq(
                    'lead_id', lead_id
                ).gte(
                    'updated_at', since.isoformat()  # Usar updated_at em vez de created_at
                ).in_(
                    'status', attempt_statuses  # Apenas executed e failed
                ).execute
            )
            
            return result.count
        except Exception as e:
            logger.error(
                f"Erro ao contar follow-ups recentes para o lead {lead_id}: {e}"
            )
            raise e

    async def update_conversation(
            self, conversation_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza dados da conversa"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()

            result = self.client.table('conversations').update(
                update_data
            ).eq('id', conversation_id).execute()

            if result.data:
                return result.data[0]

            raise Exception("Erro ao atualizar conversa")

        except Exception as e:
            emoji_logger.supabase_error(
                f"Erro ao atualizar conversa: {str(e)}",
                table="conversations"
            )
            raise

    async def update_lead_qualification(
        self, qualification_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atualiza um registro de qualificação de lead existente."""
        try:
            update_data['updated_at'] = datetime.now().isoformat()

            result = self.client.table('leads_qualifications').update(
                update_data
            ).eq('id', qualification_id).execute()

            if result.data:
                return result.data[0]
            
            logger.warning(f"Nenhuma qualificação encontrada com o ID {qualification_id} para atualizar.")
            return None

        except Exception as e:
            emoji_logger.supabase_error(
                f"Erro ao atualizar qualificação do lead: {str(e)}",
                table="leads_qualifications"
            )
            raise


supabase_client = SupabaseClient()
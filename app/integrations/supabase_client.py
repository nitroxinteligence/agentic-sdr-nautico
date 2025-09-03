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
        self.client: Client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_service_key
        )

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
            now = datetime.now().isoformat()

            result = self.client.table('follow_ups').select("*").eq(
                'status', 'pending'
            ).lte('scheduled_at', now).order('priority', desc=True).execute()

            return result.data or []

        except Exception as e:
            logger.error(f"Erro ao buscar follow-ups: {str(e)}")
            return []

    async def update_follow_up_status(
        self,
        follow_up_id: str,
        status: str,
        executed_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Atualiza status do follow-up"""
        logger.debug(f"Attempting to update follow-up {follow_up_id} to status '{status}' with data: {executed_at}")
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }

            if executed_at:
                update_data['executed_at'] = executed_at.isoformat()

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
        Conta o número de follow-ups realmente TENTADOS (executados ou falhos)
        para um lead recentemente.
        """
        try:
            # Status que não devem contar como uma tentativa.
            non_attempt_statuses = ['pending', 'queued', 'cancelled']

            result = await asyncio.to_thread(
                self.client.table('follow_ups').select(
                    'id', count='exact'
                ).eq(
                    'lead_id', lead_id
                ).gte(
                    'created_at', since.isoformat()
                ).not_.in_(
                    'status', non_attempt_statuses
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
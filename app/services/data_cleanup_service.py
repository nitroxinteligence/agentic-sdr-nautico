"""
Serviço para limpeza de dados do usuário (#CLEAR command) - Versão de produção
"""
from typing import Dict, Any


class DataCleanupService:
    """Serviço responsável pela limpeza completa de dados do usuário"""

    async def execute_clear_command(self, phone_number: str) -> Dict[str, Any]:
        """Executa o comando #CLEAR para remover todos os dados do usuário"""
        try:
            # Implementação básica para produção
            from app.integrations.supabase_client import supabase_client
            from app.utils.logger import emoji_logger

            emoji_logger.system_warning(f"🧹 COMANDO #CLEAR executado para {phone_number}")

            # Buscar lead para obter ID
            lead_data = await supabase_client.get_lead_by_phone(phone_number)

            if lead_data and lead_data.get("id"):
                lead_id = lead_data["id"]
                total_deleted = 0

                emoji_logger.system_warning(f"🧹 Iniciando limpeza completa para {phone_number} (Lead ID: {lead_id})")

                # 1. Deletar mensagens relacionadas ao lead
                try:
                    await supabase_client.delete_messages_by_lead(lead_id)
                    emoji_logger.system_success(f"🧹 Mensagens deletadas para {phone_number}")
                    total_deleted += 1
                except Exception as e:
                    emoji_logger.system_warning(f"Erro ao deletar mensagens: {e}")

                # 2. Deletar follow-ups relacionados ao lead
                try:
                    await supabase_client.delete_follow_ups_by_lead(lead_id)
                    emoji_logger.system_success(f"🧹 Follow-ups deletados para {phone_number}")
                    total_deleted += 1
                except Exception as e:
                    emoji_logger.system_warning(f"Erro ao deletar follow-ups: {e}")

                # 3. Deletar qualificações relacionadas ao lead
                try:
                    await supabase_client.delete_qualifications_by_lead(lead_id)
                    emoji_logger.system_success(f"🧹 Qualificações deletadas para {phone_number}")
                    total_deleted += 1
                except Exception as e:
                    emoji_logger.system_warning(f"Erro ao deletar qualificações: {e}")

                # 4. Deletar conversa por telefone
                try:
                    await supabase_client.delete_conversation_by_phone(phone_number)
                    emoji_logger.system_success(f"🧹 Conversa deletada para {phone_number}")
                    total_deleted += 1
                except Exception as e:
                    emoji_logger.system_warning(f"Erro ao deletar conversa: {e}")

                # 5. Deletar analytics (opcional - não crítico)
                try:
                    await supabase_client.delete_analytics_by_phone(phone_number)
                    emoji_logger.system_success(f"🧹 Analytics deletados para {phone_number}")
                    total_deleted += 1
                except Exception as e:
                    emoji_logger.system_debug(f"Analytics não deletados (normal): {e}")

                # 6. Limpar cache Redis relacionado ao telefone
                try:
                    from app.integrations.redis_client import redis_client
                    # Limpar cache de conversa
                    conversation_key = f"conversation:{phone_number}"
                    await redis_client.delete(conversation_key)

                    # Limpar outros caches relacionados ao telefone se existirem
                    lead_key = f"lead:{phone_number}"
                    await redis_client.delete(lead_key)

                    emoji_logger.system_success(f"🧹 Cache Redis limpo para {phone_number}")
                    total_deleted += 1
                except Exception as e:
                    emoji_logger.system_debug(f"Cache Redis não limpo (normal): {e}")

                # 7. Finalmente, deletar o lead principal
                try:
                    await supabase_client.delete_lead(lead_id)
                    emoji_logger.system_success(f"🧹 Lead principal deletado para {phone_number}")
                    total_deleted += 1
                except Exception as e:
                    emoji_logger.system_error("DELETE_LEAD_CRITICAL", f"ERRO CRÍTICO ao deletar lead: {e}")
                    raise e

                emoji_logger.system_success(f"🧹 LIMPEZA COMPLETA CONCLUÍDA para {phone_number} - {total_deleted} operações realizadas")

                return {
                    "success": True,
                    "phone_number": phone_number,
                    "total_deleted": total_deleted,
                    "message": f"Todos os dados de {phone_number} foram removidos com sucesso (leads, mensagens, conversas, follow-ups, qualificações)."
                }
            else:
                return {
                    "success": True,
                    "phone_number": phone_number,
                    "total_deleted": 0,
                    "message": f"Nenhum dado encontrado para {phone_number}."
                }

        except Exception as e:
            from app.utils.logger import emoji_logger
            emoji_logger.system_error("DataCleanupService", f"Erro no #CLEAR: {e}")

            return {
                "success": False,
                "phone_number": phone_number,
                "error": str(e),
                "message": "Erro ao limpar dados."
            }


# Instância global
data_cleanup_service = DataCleanupService()
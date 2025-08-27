"""
FollowUp Worker - Processa tarefas da fila de follow-ups do Redis
"""

import asyncio
from typing import Dict, Any

from app.integrations.redis_client import redis_client
from app.integrations.supabase_client import SupabaseClient
from app.agents.agentic_sdr_stateless import AgenticSDRStateless
from app.utils.logger import emoji_logger
from loguru import logger


class FollowUpWorker:
    """
    Worker que consome tarefas da fila de follow-ups e as executa.
    """

    def __init__(self):
        self.redis = redis_client
        self.db = SupabaseClient()
        self.running = False
        self.agent = AgenticSDRStateless()

    async def start(self):
        """Inicia o worker e o loop de consumo da fila."""
        if self.running:
            logger.warning("Follow-up worker já está rodando.")
            return

        await self.agent.initialize()
        self.running = True
        emoji_logger.system_ready("FollowUp Worker")
        asyncio.create_task(self._consume_loop())

    async def stop(self):
        """Para o worker."""
        self.running = False
        logger.info("Follow-up worker parado.")

    async def _consume_loop(self):
        """Loop principal que consome tarefas da fila do Redis."""
        while self.running:
            try:
                task_payload = await self.redis.dequeue(
                    "followup_tasks", timeout=10
                )
                if task_payload:
                    await self._process_task(task_payload)
            except Exception as e:
                emoji_logger.system_error(
                    "FollowUp Worker", f"Erro no loop de consumo: {e}"
                )
                await asyncio.sleep(5)

    async def _process_task(self, task_payload: Dict[str, Any]):
        """
        Processa uma única tarefa de follow-up.
        """
        # A tarefa vem aninhada em 'data' pelo redis_client
        actual_task = task_payload.get("data", {})
        followup_id = actual_task.get("followup_id")
        if not followup_id:
            logger.error(f"Task de follow-up sem ID, descartando. Payload: {task_payload}")
            return

        lock_key = f"followup_exec:{followup_id}"
        if not await self.redis.acquire_lock(lock_key, ttl=300):
            logger.warning(
                f"Execução do follow-up {followup_id} já em andamento, pulando."
            )
            return

        try:
            emoji_logger.followup_event(
                f"🚀 Processando tarefa de follow-up: {followup_id}"
            )

            message_content = await self._generate_intelligent_followup_message(
                actual_task
            )

            from app.integrations.evolution import evolution_client
            send_result = await evolution_client.send_text_message(
                phone=actual_task["phone_number"],
                message=message_content
            )

            if send_result and send_result.get("key", {}).get("id"):
                await self.db.update_follow_up_status(followup_id, 'executed')
                emoji_logger.system_success(
                    f"✅ Follow-up {followup_id} executado e enviado com sucesso."
                )
            else:
                await self.db.update_follow_up_status(followup_id, 'failed')
                emoji_logger.system_error(
                    "FollowUp Worker",
                    f"Falha ao enviar mensagem para o follow-up {followup_id}."
                )

        except Exception as e:
            emoji_logger.system_error(
                "FollowUp Worker",
                f"Erro ao processar tarefa {followup_id}: {e}"
            )
            await self.db.update_follow_up_status(followup_id, 'failed')
        finally:
            await self.redis.release_lock(lock_key)

    async def _generate_intelligent_followup_message(
            self, task_payload: Dict[str, Any]
    ) -> str:
        """
        Usa o AgenticSDRStateless para gerar uma mensagem de follow-up.
        """
        lead_id = task_payload.get("lead_id")
        followup_type = task_payload.get("followup_type", "CUSTOM")
        scheduled_message = task_payload.get("message", "")

        if not lead_id:
            emoji_logger.system_error(
                "FollowUp Worker",
                f"Task {task_payload.get('followup_id')}" + " não contém 'lead_id'."
            )
            return "Não foi possível gerar a mensagem de follow-up." # Fallback seguro

        lead_info = await self.db.get_lead_by_id(lead_id)
        conversation_id = None
        if lead_info:
            conv = await self.db.get_conversation_by_phone(lead_info.get("phone_number"))
            if conv:
                conversation_id = conv.get("id")

        conversation_history = await self.db.get_conversation_messages(
            conversation_id
        ) if conversation_id else []

        # Constrói um resumo do histórico para o LLM
        history_summary = ""
        if conversation_history:
            # Pega as últimas 5 mensagens para um resumo conciso
            last_messages = conversation_history[-5:]
            for msg in last_messages:
                role = "Você" if msg.get("role") == "assistant" else "O Lead"
                content = msg.get("content")
                # Se o conteúdo for uma lista (multimodal), pega apenas o texto
                if isinstance(content, list):
                    text_parts = [p.get("text") for p in content if p.get("type") == "text"]
                    content = " ".join(text_parts) if text_parts else "[Mídia]"
                history_summary += f"{role}: {content}\n"

        # Informações do lead para o prompt
        lead_name = lead_info.get("name", "o lead")
        bill_value = lead_info.get("bill_value", "não informado")
        chosen_flow = lead_info.get("chosen_flow", "não definido")

        # Prompt para o LLM
        prompt_to_llm = f"""
        Você é a Helen Vieira, Coordenadora de Qualificação Sênior da SolarPrime. Sua tarefa é gerar uma mensagem de follow-up para um lead. O tipo de follow-up é '{followup_type}'.

        Informações do Lead:
        - Nome: {lead_name}
        - Valor da Conta de Energia: R${bill_value}
        - Fluxo Escolhido: {chosen_flow}

        Histórico Recente da Conversa (últimas 5 mensagens):
        {history_summary}

        Instruções para a Mensagem:
        - O objetivo é reengajar {lead_name} ou enviar um lembrete de reunião, dependendo do 'followup_type'.
        - Seja acolhedora, técnica e consultiva, com um toque nordestino.
        - Use o contexto do histórico para tornar a mensagem relevante e personalizada.
        - Se 'followup_type' for 'IMMEDIATE_REENGAGEMENT' ou 'DAILY_NURTURING', o objetivo é reabrir a conversa de forma natural, referenciando o último ponto.
        - Se 'followup_type' for 'MEETING_REMINDER', use a 'scheduled_message' fornecida (que deve conter o link da reunião) e adapte o tom.
        - Mantenha a mensagem concisa e direta.
        - NUNCA use emojis na mensagem.
        - NUNCA use markdown como negrito (*texto*) ou itálico (_texto_).
        - Apenas a mensagem final, sem tags de raciocínio ou ferramentas.
        """
        
        # Se houver uma mensagem pré-definida (para lembretes de reunião, por exemplo), use-a
        if scheduled_message and followup_type == 'MEETING_REMINDER':
            emoji_logger.system_info(f"Usando mensagem pré-definida para MEETING_REMINDER: {scheduled_message}")
            return scheduled_message

        execution_context = {
            "conversation_history": conversation_history,
            "lead_info": lead_info or {},
            "phone": task_payload.get("phone_number"),
            "conversation_id": conversation_id,
        }

        response_text = await self.agent._generate_response(
            message=prompt_to_llm,
            context={},
            lead_info=lead_info or {},
            conversation_history=conversation_history,
            execution_context=execution_context,
            is_followup=True
        )

        from app.api.webhooks import extract_final_response
        return extract_final_response(response_text)


async def main():
    """Função principal para iniciar o worker."""
    worker = FollowUpWorker()
    await worker.start()
    while worker.running:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
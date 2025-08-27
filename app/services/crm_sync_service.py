# app/services/crm_sync_service.py

from typing import Dict, Any, List, Optional
from app.utils.logger import emoji_logger

class CRMDataSync:
    """
    Centraliza a lógica para decidir quais dados do lead devem ser
    sincronizados com o Kommo CRM com base no estado da conversa.
    """

    def __init__(self):
        # Mapeamento direto do valor do campo 'chosen_flow' para a tag correspondente.
        self.solution_to_tag_map = {
            "Instalação Usina Própria": "Instalação Usina Própria",
            "Aluguel de Lote": "Aluguel de Lote",
            "Compra com Desconto": "Compra com Desconto",
            "Usina Investimento": "Usina Investimento",
        }

    def get_update_payload(
        self,
        lead_info: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Analisa o lead e o histórico para gerar um payload de atualização para o CRM.

        Retorna um dicionário com os dados a serem atualizados ou None se nenhuma
        atualização for necessária.
        """
        update_payload = {}
        tags_to_add = []

        # 1. Sincronizar "SOLUÇAO SOLAR" e a tag correspondente
        chosen_flow = lead_info.get("chosen_flow")
        if chosen_flow:
            update_payload["chosen_flow"] = chosen_flow
            tag = self.solution_to_tag_map.get(chosen_flow)
            if tag:
                tags_to_add.append(tag)

        # 2. Sincronizar "NOME" do lead
        name = lead_info.get("name")
        if name:
            update_payload["name"] = name

        # 3. Sincronizar "VALOR CONTA DE ENERGIA"
        bill_value = lead_info.get("bill_value")
        if bill_value:
            update_payload["bill_value"] = bill_value
        
        # 4. Sincronizar "WHATSAPP" (se necessário, embora geralmente seja pego no início)
        phone = lead_info.get("phone_number")
        if phone:
            # O campo 'phone' no Kommo é gerenciado pelo 'whatsapp' no nosso mapeamento
            update_payload["phone"] = phone

        # 5. Sincronizar "QUALIFICATION_SCORE"
        qualification_score = lead_info.get("qualification_score")
        if qualification_score is not None:
            update_payload["qualification_score"] = qualification_score

        # 6. Lógica para tag "sem-resposta" e mudança de estágio
        # (Esta lógica pode ser mais complexa e depender do monitor de conversas)
        # Exemplo simples: se a última mensagem for do agente e não houver resposta por um tempo.
        # A implementação real virá da análise do estado do lead.
        if lead_info.get("current_stage") == "NAO_INTERESSADO":
            tags_to_add.append("sem-resposta")
            update_payload["current_stage"] = "NAO_INTERESSADO" # Garante que o estágio seja enviado

        # Adiciona as tags ao payload se houver alguma
        if tags_to_add:
            # Usamos set para garantir que não haja tags duplicadas
            update_payload["tags"] = list(set(tags_to_add))

        if not update_payload:
            emoji_logger.system_debug("CRM Sync: Nenhuma atualização necessária.")
            return None

        emoji_logger.system_info("CRM Sync: Payload de atualização gerado.", payload=update_payload)
        return update_payload

# Instância singleton
crm_sync_service = CRMDataSync()

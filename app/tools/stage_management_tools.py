"""
Stage Management Tools - Sistema de movimentação de estágios no CRM
Implementa o fluxo atualizado do Náutico:
Novo Lead → Em Qualificação → Qualificado/Desqualificado/Atendimento Humano
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.integrations.supabase_client import supabase_client
from app.utils.logger import emoji_logger


class StageManagementTools:
    """Ferramentas para gerenciar movimentação de estágios no CRM"""

    def __init__(self, crm_service=None):
        self.crm_service = crm_service
        self.stage_map = {
            "novo_lead": settings.kommo_novo_lead_stage_id,
            "em_qualificacao": settings.kommo_em_qualificacao_stage_id, 
            "qualificado": settings.kommo_qualificado_stage_id,
            "desqualificado": settings.kommo_desqualificado_stage_id,
            "atendimento_humano": settings.kommo_human_handoff_stage_id
        }

    async def move_to_em_qualificacao(
        self, 
        lead_info: Dict[str, Any], 
        notes: str = "Lead iniciou qualificação - Marina entrando na conversa"
    ) -> Dict[str, Any]:
        """
        Move lead para estágio "Em Qualificação"
        Usado na ETAPA 0 após o áudio do presidente
        """
        try:
            # Para operações no CRM, usar kommo_lead_id (inteiro), para Supabase usar id (UUID)
            kommo_lead_id = lead_info.get("kommo_lead_id")
            supabase_lead_id = lead_info.get("id")
            phone = lead_info.get("phone") or lead_info.get("phone_number")
            
            if not kommo_lead_id and not supabase_lead_id:
                emoji_logger.service_warning("ID do lead não encontrado para movimentação de estágio")
                return {"success": False, "message": "Lead ID não encontrado"}

            # Atualizar no CRM se disponível e tiver kommo_lead_id
            if self.crm_service and kommo_lead_id:
                result = await self.crm_service.update_lead_stage(
                    lead_id=str(kommo_lead_id),
                    stage_name="em_qualificacao",
                    notes=notes,
                    phone_number=phone
                )
                
                if result.get("success"):
                    emoji_logger.service_info(f"✅ Lead {kommo_lead_id} movido para 'Em Qualificação' no CRM")
                else:
                    emoji_logger.service_warning(f"Falha ao mover lead {kommo_lead_id} no CRM: {result.get('message')}")
            elif self.crm_service and not kommo_lead_id:
                emoji_logger.service_warning("Lead não tem kommo_lead_id - pulando atualização no CRM")

            # Atualizar no Supabase se tiver supabase_lead_id
            if supabase_lead_id:
                try:
                    update_data = {
                        "current_stage": "EM_QUALIFICACAO", 
                        "qualification_status": "PENDING"
                    }
                    await supabase_client.update_lead(supabase_lead_id, update_data)
                    emoji_logger.service_success(f"Lead {supabase_lead_id} atualizado no Supabase - Em Qualificação")
                except Exception as e:
                    emoji_logger.service_error(f"Erro ao atualizar lead no Supabase: {e}")

            return {
                "success": True,
                "message": "Lead movido para Em Qualificação",
                "stage": "em_qualificacao", 
                "kommo_lead_id": kommo_lead_id,
                "supabase_lead_id": supabase_lead_id
            }

        except Exception as e:
            emoji_logger.service_error(f"Erro ao mover lead para Em Qualificação: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    async def move_to_qualificado(
        self, 
        lead_info: Dict[str, Any], 
        payment_value: Optional[str] = None,
        payment_valid: bool = True,
        notes: str = "Lead qualificado - Pagamento confirmado"
    ) -> Dict[str, Any]:
        """
        Move lead para estágio "Qualificado"
        Usado na ETAPA 5 após validação do comprovante
        """
        try:
            # Para operações no CRM, usar kommo_lead_id (inteiro), para Supabase usar id (UUID)
            kommo_lead_id = lead_info.get("kommo_lead_id")
            supabase_lead_id = lead_info.get("id")
            phone = lead_info.get("phone") or lead_info.get("phone_number")
            
            if not kommo_lead_id and not supabase_lead_id:
                emoji_logger.service_warning("ID do lead não encontrado para qualificação")
                return {"success": False, "message": "Lead ID não encontrado"}

            # Enriquecer notes com informações do pagamento
            if payment_value:
                notes = f"{notes} - Valor: R$ {payment_value}"
            
            # Atualizar no CRM se disponível e tiver kommo_lead_id
            if self.crm_service and kommo_lead_id:
                result = await self.crm_service.update_lead_stage(
                    lead_id=str(kommo_lead_id),
                    stage_name="qualificado", 
                    notes=notes,
                    phone_number=phone
                )
                
                if result.get("success"):
                    emoji_logger.service_info(f"✅ Lead {kommo_lead_id} QUALIFICADO no CRM")
                else:
                    emoji_logger.service_warning(f"Falha ao qualificar lead {kommo_lead_id} no CRM: {result.get('message')}")
            elif self.crm_service and not kommo_lead_id:
                emoji_logger.service_warning("Lead não tem kommo_lead_id - pulando atualização no CRM")

            # Atualizar no Supabase se tiver supabase_lead_id
            if supabase_lead_id:
                try:
                    # 1. Atualizar tabela leads
                    lead_update_data = {
                        "current_stage": "QUALIFICADO"
                    }
                    
                    if payment_value:
                        lead_update_data["bill_value"] = payment_value
                        lead_update_data["payment_confirmed"] = payment_valid
                        
                    await supabase_client.update_lead(supabase_lead_id, lead_update_data)
                    
                    # 2. Criar/atualizar qualificação na tabela leads_qualifications
                    qualification_data = {
                        "lead_id": supabase_lead_id,
                        "qualification_status": "QUALIFIED", 
                        "qualified_at": datetime.now().isoformat(),
                        "current_stage": "QUALIFICADO"
                    }
                    
                    if payment_value:
                        qualification_data["notes"] = f"Pagamento confirmado: R$ {payment_value}"
                        
                    await supabase_client.create_lead_qualification(qualification_data)
                    emoji_logger.service_success(f"Lead {supabase_lead_id} QUALIFICADO no Supabase (leads + qualifications)")
                except Exception as e:
                    emoji_logger.service_error(f"Erro ao qualificar lead no Supabase: {e}")

            return {
                "success": True,
                "message": "Lead qualificado com sucesso",
                "stage": "qualificado",
                "kommo_lead_id": kommo_lead_id,
                "supabase_lead_id": supabase_lead_id,
                "payment_value": payment_value
            }

        except Exception as e:
            emoji_logger.service_error(f"Erro ao qualificar lead: {e}")
            return {
                "success": False, 
                "message": f"Erro: {str(e)}"
            }

    async def move_to_desqualificado(
        self,
        lead_info: Dict[str, Any],
        reason: str = "Sem resposta após follow-ups",
        notes: str = "Lead desqualificado automaticamente"
    ) -> Dict[str, Any]:
        """
        Move lead para estágio "Desqualificado"  
        Usado após 48h sem resposta ou resposta negativa
        """
        try:
            # Para operações no CRM, usar kommo_lead_id (inteiro), para Supabase usar id (UUID)
            kommo_lead_id = lead_info.get("kommo_lead_id")
            supabase_lead_id = lead_info.get("id")
            phone = lead_info.get("phone") or lead_info.get("phone_number")
            
            if not kommo_lead_id and not supabase_lead_id:
                emoji_logger.service_warning("ID do lead não encontrado para desqualificação")
                return {"success": False, "message": "Lead ID não encontrado"}

            full_notes = f"{notes} - Motivo: {reason}"
            
            # Atualizar no CRM se disponível e tiver kommo_lead_id
            if self.crm_service and kommo_lead_id:
                result = await self.crm_service.update_lead_stage(
                    lead_id=str(kommo_lead_id),
                    stage_name="desqualificado",
                    notes=full_notes,
                    phone_number=phone
                )
                
                if result.get("success"):
                    emoji_logger.service_info(f"❌ Lead {kommo_lead_id} DESQUALIFICADO no CRM")
                else:
                    emoji_logger.service_warning(f"Falha ao desqualificar lead {kommo_lead_id} no CRM: {result.get('message')}")
            elif self.crm_service and not kommo_lead_id:
                emoji_logger.service_warning("Lead não tem kommo_lead_id - pulando atualização no CRM")

            # Atualizar no Supabase se tiver supabase_lead_id
            if supabase_lead_id:
                try:
                    # 1. Atualizar tabela leads
                    lead_update_data = {
                        "current_stage": "DESQUALIFICADO"
                    }
                    await supabase_client.update_lead(supabase_lead_id, lead_update_data)
                    
                    # 2. Criar/atualizar qualificação na tabela leads_qualifications
                    qualification_data = {
                        "lead_id": supabase_lead_id,
                        "qualification_status": "NOT_QUALIFIED",
                        "current_stage": "DESQUALIFICADO",
                        "notes": f"Desqualificado em {datetime.now().isoformat()}: {reason}"
                    }
                    
                    await supabase_client.create_lead_qualification(qualification_data)
                    emoji_logger.service_success(f"Lead {supabase_lead_id} DESQUALIFICADO no Supabase (leads + qualifications)")
                except Exception as e:
                    emoji_logger.service_error(f"Erro ao desqualificar lead no Supabase: {e}")

            return {
                "success": True,
                "message": "Lead desqualificado",
                "stage": "desqualificado",
                "kommo_lead_id": kommo_lead_id,
                "supabase_lead_id": supabase_lead_id,
                "reason": reason
            }

        except Exception as e:
            emoji_logger.service_error(f"Erro ao desqualificar lead: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    async def move_to_atendimento_humano(
        self,
        lead_info: Dict[str, Any], 
        reason: str = "Encaminhado para especialista",
        notes: str = "Lead necessita atendimento humano especializado"
    ) -> Dict[str, Any]:
        """
        Move lead para estágio "Atendimento Humano"
        Pausa interações da IA
        """
        try:
            # Para operações no CRM, usar kommo_lead_id (inteiro), para Supabase usar id (UUID)
            kommo_lead_id = lead_info.get("kommo_lead_id")
            supabase_lead_id = lead_info.get("id")
            phone = lead_info.get("phone") or lead_info.get("phone_number")
            
            if not kommo_lead_id and not supabase_lead_id:
                emoji_logger.service_warning("ID do lead não encontrado para handoff")
                return {"success": False, "message": "Lead ID não encontrado"}

            full_notes = f"{notes} - Motivo: {reason}"
            
            # Atualizar no CRM se disponível e tiver kommo_lead_id
            if self.crm_service and kommo_lead_id:
                result = await self.crm_service.update_lead_stage(
                    lead_id=str(kommo_lead_id),
                    stage_name="atendimento_humano",
                    notes=full_notes, 
                    phone_number=phone
                )
                
                if result.get("success"):
                    emoji_logger.service_info(f"👤 Lead {kommo_lead_id} encaminhado para ATENDIMENTO HUMANO no CRM")
                else:
                    emoji_logger.service_warning(f"Falha ao encaminhar lead {kommo_lead_id} no CRM: {result.get('message')}")
            elif self.crm_service and not kommo_lead_id:
                emoji_logger.service_warning("Lead não tem kommo_lead_id - pulando atualização no CRM")

            # Atualizar no Supabase se tiver supabase_lead_id
            if supabase_lead_id:
                try:
                    update_data = {
                        "current_stage": "ATENDIMENTO_HUMANO", 
                        "qualification_status": "PENDING",
                        "handoff_at": datetime.now().isoformat(),
                        "handoff_reason": reason,
                        "ai_paused": True  # Flag para pausar IA
                    }
                    await supabase_client.update_lead(supabase_lead_id, update_data)
                    emoji_logger.service_success(f"Lead {supabase_lead_id} encaminhado para ATENDIMENTO HUMANO no Supabase") 
                except Exception as e:
                    emoji_logger.service_error(f"Erro ao encaminhar lead no Supabase: {e}")

            return {
                "success": True,
                "message": "Lead encaminhado para atendimento humano",
                "stage": "atendimento_humano",
                "kommo_lead_id": kommo_lead_id,
                "supabase_lead_id": supabase_lead_id,
                "reason": reason,
                "ai_paused": True
            }

        except Exception as e:
            emoji_logger.service_error(f"Erro ao encaminhar lead para atendimento humano: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    async def check_human_handoff_status(self, lead_info: Dict[str, Any]) -> bool:
        """
        Verifica se o lead está no estágio "Atendimento Humano"
        Retorna True se a IA deve ficar em silêncio
        """
        try:
            current_stage = lead_info.get("current_stage", "").upper()
            ai_paused = lead_info.get("ai_paused", False)
            
            # Verificar se está em atendimento humano
            if current_stage == "ATENDIMENTO_HUMANO" or ai_paused:
                emoji_logger.service_info("🔇 Lead em ATENDIMENTO HUMANO - IA pausada")
                return True
                
            return False
            
        except Exception as e:
            emoji_logger.service_error(f"Erro ao verificar status de handoff: {e}")
            return False

    def get_stage_info(self, stage_name: str) -> Dict[str, Any]:
        """Retorna informações sobre um estágio específico"""
        stage_info = {
            "novo_lead": {
                "name": "Novo Lead",
                "description": "Lead recém-criado, aguardando primeira interação",
                "next_stages": ["em_qualificacao"]
            },
            "em_qualificacao": {
                "name": "Em Qualificação", 
                "description": "Marina iniciou conversa e está qualificando o lead",
                "next_stages": ["qualificado", "desqualificado", "atendimento_humano"]
            },
            "qualificado": {
                "name": "Qualificado",
                "description": "Lead confirmou pagamento e foi aprovado",
                "next_stages": []
            },
            "desqualificado": {
                "name": "Desqualificado",
                "description": "Lead não demonstrou interesse ou não respondeu",
                "next_stages": []
            },
            "atendimento_humano": {
                "name": "Atendimento Humano",
                "description": "Lead precisa de atendimento especializado - IA pausada",
                "next_stages": ["em_qualificacao", "qualificado", "desqualificado"]
            }
        }
        
        return stage_info.get(stage_name.lower(), {
            "name": stage_name,
            "description": "Estágio não reconhecido",
            "next_stages": []
        })
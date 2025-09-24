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
        # Se não foi passado um serviço, usar o queue service
        if crm_service is None:
            from app.services.kommo_queue_service import kommo_queue_service
            self.crm_service = kommo_queue_service
        else:
            self.crm_service = crm_service
        self.stage_map = {
            "novo_lead": settings.kommo_novo_lead_stage_id,
            "em_qualificacao": settings.kommo_em_qualificacao_stage_id, 
            "qualificado": settings.kommo_qualificado_stage_id,
            "desqualificado": settings.kommo_desqualificado_stage_id,
            "atendimento_humano": settings.kommo_human_handoff_stage_id
        }

    async def _validate_and_clean_kommo_lead(self, kommo_lead_id: str, supabase_lead_id: str = None) -> bool:
        """
        Valida se o lead existe no Kommo. Se não existir, limpa o kommo_lead_id do Supabase.
        Retorna True se o lead existir, False caso contrário.
        """
        if not self.crm_service or not kommo_lead_id:
            return False
            
        lead_exists = await self.crm_service.get_lead_by_id(str(kommo_lead_id))
        
        if not lead_exists:
            emoji_logger.service_warning(f"Lead {kommo_lead_id} não existe mais no Kommo - limpando kommo_lead_id")
            # Limpar o kommo_lead_id do Supabase já que não existe mais no Kommo
            if supabase_lead_id:
                from app.integrations.supabase_client import supabase_client
                await supabase_client.update_lead(supabase_lead_id, {"kommo_lead_id": None})
            return False
            
        return True

    async def move_to_em_qualificacao(
        self, 
        lead_info: Dict[str, Any], 
        notes: str = "Lead iniciou qualificação - Laura entrando na conversa"
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
                if await self._validate_and_clean_kommo_lead(kommo_lead_id, supabase_lead_id):
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
        payment_valid: bool = False,  # MUDANÇA: Padrão False para ser mais restritivo
        notes: str = "Lead qualificado - Pagamento confirmado"
    ) -> Dict[str, Any]:
        """
        Move lead para estágio "Qualificado"
        IMPORTANTE: Só deve ser usado após validação real de comprovante de pagamento
        
        Args:
            lead_info: Informações do lead
            payment_value: Valor do pagamento (obrigatório)
            payment_valid: Deve ser True APENAS após validação de comprovante (padrão False)
            notes: Observações sobre a qualificação
        """
        try:
            # VALIDAÇÃO CRÍTICA: Não qualificar sem pagamento válido
            if not payment_valid:
                emoji_logger.service_error(
                    "🔒 QUALIFICAÇÃO BLOQUEADA - payment_valid=False. "
                    "Lead só pode ser qualificado com payment_valid=True após validação de comprovante."
                )
                return {
                    "success": False,
                    "message": "Qualificação rejeitada - payment_valid deve ser True após validação de comprovante"
                }
            
            if not payment_value:
                emoji_logger.service_error(
                    "🔒 QUALIFICAÇÃO BLOQUEADA - payment_value não fornecido. "
                    "Lead só pode ser qualificado com valor de pagamento válido."
                )
                return {
                    "success": False,
                    "message": "Qualificação rejeitada - payment_value é obrigatório"
                }
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
                if await self._validate_and_clean_kommo_lead(kommo_lead_id, supabase_lead_id):
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
                        lead_update_data["payment_value"] = payment_value
                        lead_update_data["is_valid_nautico_payment"] = payment_valid
                        
                        # Incluir nome do pagador se disponível no lead_info
                        payer_name = lead_info.get("payer_name")
                        if payer_name:
                            lead_update_data["payer_name"] = payer_name
                        
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

            # IMPORTANTE: Cancelar follow-ups pendentes quando lead é qualificado
            await StageManagementTools._cancel_pending_followups(supabase_lead_id, "Lead qualificado - não precisa mais de follow-ups")

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
                if await self._validate_and_clean_kommo_lead(kommo_lead_id, supabase_lead_id):
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
                if await self._validate_and_clean_kommo_lead(kommo_lead_id, supabase_lead_id):
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

            # IMPORTANTE: Cancelar follow-ups pendentes quando lead vai para atendimento humano
            await StageManagementTools._cancel_pending_followups(supabase_lead_id, "Lead em atendimento humano - IA pausada")

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
                "description": "Laura iniciou conversa e está qualificando o lead",
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

    @staticmethod
    async def _cancel_pending_followups(lead_id: str, reason: str = "Status alterado") -> Dict[str, Any]:
        """
        Cancela todos os follow-ups pendentes para um lead específico
        """
        try:
            # Buscar follow-ups pendentes para este lead
            from app.integrations.supabase_client import supabase_client
            
            pending_followups = supabase_client.client.table('follow_ups').select('id').eq(
                'lead_id', lead_id
            ).eq('status', 'pending').execute()
            
            if pending_followups.data:
                followup_ids = [fu['id'] for fu in pending_followups.data]
                
                # Cancelar todos os follow-ups pendentes
                cancel_result = supabase_client.client.table('follow_ups').update({
                    'status': 'cancelled',
                    'error_reason': reason,
                    'updated_at': datetime.now().isoformat()
                }).in_('id', followup_ids).execute()
                
                emoji_logger.service_success(f"✅ {len(followup_ids)} follow-ups cancelados para lead {lead_id[:8]}... - Motivo: {reason}")
                
                return {
                    "success": True,
                    "cancelled_count": len(followup_ids),
                    "reason": reason
                }
            else:
                emoji_logger.service_info(f"ℹ️ Nenhum follow-up pendente encontrado para lead {lead_id[:8]}...")
                return {
                    "success": True, 
                    "cancelled_count": 0,
                    "reason": "Nenhum follow-up pendente"
                }
                
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao cancelar follow-ups para lead {lead_id[:8]}...: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }
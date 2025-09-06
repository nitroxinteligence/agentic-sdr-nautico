"""
Follow-up Tools Náutico - Sistema de follow-ups automáticos
Implementa o protocolo do prompt atualizado:
- 4h: "Opa, [Nome]! Passando só pra saber se ficou alguma dúvida..."
- 24h: "E aí, tudo certo? Deu pra pensar na nossa conversa..."  
- 48h: "Fala, [Nome]. Essa é minha última tentativa..." + Desqualificar
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pytz
from app.config import settings
from app.utils.logger import emoji_logger
from app.tools.stage_management_tools import StageManagementTools


class FollowUpNauticoTools:
    """Ferramentas de follow-up específicas do Náutico"""

    def __init__(self, followup_service=None):
        self.followup_service = followup_service
        self.stage_tools = StageManagementTools()
        
        # Templates de mensagem do prompt atualizado
        self.follow_up_templates = {
            "4h": "Opa, {name}! Passando só pra saber se ficou alguma dúvida sobre o que a gente conversou. Tô por aqui visse?",
            "24h": "E aí, tudo certo? Deu pra pensar na nossa conversa sobre fortalecer o Timão? Qualquer coisa é só dar um alô.",
            "48h": "Fala, {name}. Essa é minha última tentativa. Se ainda quiser fazer parte do nosso time de sócios, me chama aqui. Grande abraço alvirrubro!"
        }

    async def schedule_nautico_followups(
        self, 
        lead_info: Dict[str, Any], 
        phone_number: str
    ) -> Dict[str, Any]:
        """
        Agenda os 3 follow-ups automáticos do Náutico conforme protocolo
        """
        try:
            if not self.followup_service:
                emoji_logger.service_warning("Follow-up service não disponível")
                return {"success": False, "message": "Serviço de follow-up não configurado"}

            lead_name = lead_info.get("name", "")
            if not lead_name:
                lead_name = "amigo"

            scheduled_followups = []

            # Follow-up 1: 4 horas
            message_4h = self.follow_up_templates["4h"].format(name=lead_name)
            result_4h = await self.followup_service.schedule_followup(
                phone_number=phone_number,
                message=message_4h,
                delay_hours=4,
                lead_info=lead_info
            )
            if result_4h.get("success"):
                scheduled_followups.append({
                    "delay": "4h", 
                    "followup_id": result_4h.get("followup_id"),
                    "message": message_4h
                })

            # Follow-up 2: 24 horas  
            message_24h = self.follow_up_templates["24h"]
            result_24h = await self.followup_service.schedule_followup(
                phone_number=phone_number,
                message=message_24h,
                delay_hours=24,
                lead_info=lead_info
            )
            if result_24h.get("success"):
                scheduled_followups.append({
                    "delay": "24h",
                    "followup_id": result_24h.get("followup_id"),
                    "message": message_24h
                })

            # Follow-up 3: 48 horas (último + desqualificar)
            message_48h = self.follow_up_templates["48h"].format(name=lead_name)
            result_48h = await self.followup_service.schedule_followup(
                phone_number=phone_number,
                message=message_48h,
                delay_hours=48,
                lead_info=lead_info
            )
            if result_48h.get("success"):
                scheduled_followups.append({
                    "delay": "48h",
                    "followup_id": result_48h.get("followup_id"),
                    "message": message_48h,
                    "final": True,
                    "action": "desqualificar_se_sem_resposta"
                })

            emoji_logger.followup_event(
                f"✅ {len(scheduled_followups)} follow-ups do Náutico agendados para {phone_number}"
            )

            return {
                "success": True,
                "scheduled_followups": scheduled_followups,
                "total": len(scheduled_followups),
                "message": f"{len(scheduled_followups)} follow-ups agendados"
            }

        except Exception as e:
            emoji_logger.service_error(f"Erro ao agendar follow-ups do Náutico: {e}")
            return {
                "success": False,
                "message": f"Erro ao agendar follow-ups: {str(e)}"
            }

    async def process_final_followup_response(
        self,
        lead_info: Dict[str, Any],
        has_response: bool = False
    ) -> Dict[str, Any]:
        """
        Processa resposta ao follow-up final (48h)
        Se não houver resposta, desqualifica automaticamente
        """
        try:
            if not has_response:
                # Após 48h sem resposta, desqualificar
                emoji_logger.followup_event(
                    f"📝 DESQUALIFICAÇÃO AUTOMÁTICA - Lead {lead_info.get('id')} sem resposta após follow-ups"
                )
                
                result = await self.stage_tools.move_to_desqualificado(
                    lead_info=lead_info,
                    reason="Sem resposta após 48h + follow-ups",
                    notes="Desqualificado automaticamente pelo protocolo de follow-up do Náutico"
                )
                
                return {
                    "success": True,
                    "action": "desqualified",
                    "stage_result": result,
                    "message": "Lead desqualificado após follow-ups sem resposta"
                }
            else:
                # Lead respondeu, continuar conversa normalmente
                emoji_logger.followup_event(
                    f"✅ RESPOSTA RECEBIDA - Lead {lead_info.get('id')} respondeu após follow-up"
                )
                
                return {
                    "success": True,
                    "action": "continue",
                    "message": "Lead respondeu - conversa reativada"
                }

        except Exception as e:
            emoji_logger.service_error(f"Erro ao processar follow-up final: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    async def cancel_pending_followups(
        self,
        lead_info: Dict[str, Any],
        phone_number: str,
        reason: str = "Lead respondeu"
    ) -> Dict[str, Any]:
        """
        Cancela follow-ups pendentes quando lead responde
        """
        try:
            if not self.followup_service:
                return {"success": False, "message": "Serviço de follow-up não disponível"}

            # Buscar follow-ups pendentes para este lead
            pending = await self.followup_service.get_pending_followups()
            cancelled_count = 0
            
            for followup in pending:
                if followup.get("phone_number") == phone_number.replace("+", "").replace("-", "").replace(" ", ""):
                    # Marcar como cancelado/executado para evitar envio
                    try:
                        await self.followup_service.cancel_followup(
                            followup.get("id"),
                            reason=reason
                        )
                        cancelled_count += 1
                    except Exception as e:
                        emoji_logger.service_warning(f"Erro ao cancelar follow-up {followup.get('id')}: {e}")

            emoji_logger.followup_event(
                f"🚫 {cancelled_count} follow-ups cancelados para {phone_number} - Motivo: {reason}"
            )

            return {
                "success": True,
                "cancelled_count": cancelled_count,
                "message": f"{cancelled_count} follow-ups cancelados"
            }

        except Exception as e:
            emoji_logger.service_error(f"Erro ao cancelar follow-ups: {e}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    def get_followup_template(self, delay: str, name: str = "amigo") -> str:
        """Retorna template de follow-up formatado"""
        template = self.follow_up_templates.get(delay, "")
        if "{name}" in template:
            return template.format(name=name)
        return template

    def get_followup_schedule(self) -> Dict[str, Any]:
        """Retorna cronograma de follow-ups do Náutico"""
        return {
            "protocol": "Náutico Follow-up Protocol",
            "stages": [
                {
                    "delay": "4h",
                    "hours": 4,
                    "template": self.follow_up_templates["4h"],
                    "type": "check_in"
                },
                {
                    "delay": "24h", 
                    "hours": 24,
                    "template": self.follow_up_templates["24h"],
                    "type": "reminder"
                },
                {
                    "delay": "48h",
                    "hours": 48, 
                    "template": self.follow_up_templates["48h"],
                    "type": "final_attempt",
                    "action_if_no_response": "desqualificar"
                }
            ],
            "total_followups": 3,
            "max_duration": "48 horas"
        }
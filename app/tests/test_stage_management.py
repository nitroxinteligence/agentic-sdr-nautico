"""
Testes para o sistema de gerenciamento de estágios do Náutico
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.tools.stage_management_tools import StageManagementTools
from app.tools.followup_nautico_tools import FollowUpNauticoTools


class TestStageManagementTools:
    """Testes para StageManagementTools"""

    @pytest.fixture
    def mock_crm_service(self):
        """Mock do CRM service"""
        crm = Mock()
        crm.update_lead_stage = AsyncMock(return_value={
            "success": True, 
            "message": "Lead movido com sucesso"
        })
        return crm

    @pytest.fixture
    def stage_tools(self, mock_crm_service):
        """Instância das ferramentas de estágio com mocks"""
        return StageManagementTools(mock_crm_service)

    @pytest.fixture
    def sample_lead_info(self):
        """Lead de exemplo para testes"""
        return {
            "id": "12345",
            "kommo_lead_id": "67890",
            "name": "João Torcedor",
            "phone": "5581999999999",
            "phone_number": "5581999999999"
        }

    @pytest.mark.asyncio
    async def test_move_to_em_qualificacao(self, stage_tools, sample_lead_info, mock_crm_service):
        """Testa movimentação para Em Qualificação"""
        with patch('app.tools.stage_management_tools.supabase_client') as mock_supabase:
            mock_supabase.update_lead = AsyncMock()
            
            result = await stage_tools.move_to_em_qualificacao(sample_lead_info)
            
            # Verificar resultado
            assert result["success"] is True
            assert result["stage"] == "em_qualificacao"
            assert "12345" in str(result["lead_id"])
            
            # Verificar chamadas
            mock_crm_service.update_lead_stage.assert_called_once()
            mock_supabase.update_lead.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_to_qualificado(self, stage_tools, sample_lead_info, mock_crm_service):
        """Testa qualificação de lead com pagamento"""
        with patch('app.tools.stage_management_tools.supabase_client') as mock_supabase:
            mock_supabase.update_lead = AsyncMock()
            
            result = await stage_tools.move_to_qualificado(
                sample_lead_info, 
                payment_value="39,90",
                payment_valid=True
            )
            
            # Verificar resultado
            assert result["success"] is True
            assert result["stage"] == "qualificado"
            assert result["payment_value"] == "39,90"
            
            # Verificar chamadas
            mock_crm_service.update_lead_stage.assert_called_once()
            mock_supabase.update_lead.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_to_desqualificado(self, stage_tools, sample_lead_info, mock_crm_service):
        """Testa desqualificação de lead"""
        with patch('app.tools.stage_management_tools.supabase_client') as mock_supabase:
            mock_supabase.update_lead = AsyncMock()
            
            result = await stage_tools.move_to_desqualificado(
                sample_lead_info,
                reason="Sem resposta após follow-ups"
            )
            
            # Verificar resultado
            assert result["success"] is True
            assert result["stage"] == "desqualificado"
            assert result["reason"] == "Sem resposta após follow-ups"
            
            # Verificar chamadas
            mock_crm_service.update_lead_stage.assert_called_once()
            mock_supabase.update_lead.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_to_atendimento_humano(self, stage_tools, sample_lead_info, mock_crm_service):
        """Testa encaminhamento para atendimento humano"""
        with patch('app.tools.stage_management_tools.supabase_client') as mock_supabase:
            mock_supabase.update_lead = AsyncMock()
            
            result = await stage_tools.move_to_atendimento_humano(
                sample_lead_info,
                reason="Pergunta muito específica"
            )
            
            # Verificar resultado
            assert result["success"] is True
            assert result["stage"] == "atendimento_humano"
            assert result["ai_paused"] is True
            
            # Verificar chamadas
            mock_crm_service.update_lead_stage.assert_called_once()
            mock_supabase.update_lead.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_human_handoff_status(self, stage_tools):
        """Testa detecção de atendimento humano"""
        # Lead em atendimento humano
        lead_handoff = {
            "current_stage": "ATENDIMENTO_HUMANO",
            "ai_paused": True
        }
        
        result = await stage_tools.check_human_handoff_status(lead_handoff)
        assert result is True
        
        # Lead normal
        lead_normal = {
            "current_stage": "EM_QUALIFICACAO",
            "ai_paused": False
        }
        
        result = await stage_tools.check_human_handoff_status(lead_normal)
        assert result is False

    def test_get_stage_info(self, stage_tools):
        """Testa informações dos estágios"""
        info = stage_tools.get_stage_info("em_qualificacao")
        
        assert info["name"] == "Em Qualificação"
        assert "qualificado" in info["next_stages"]
        assert "desqualificado" in info["next_stages"]
        assert "atendimento_humano" in info["next_stages"]


class TestFollowUpNauticoTools:
    """Testes para FollowUpNauticoTools"""

    @pytest.fixture
    def mock_followup_service(self):
        """Mock do serviço de follow-up"""
        service = Mock()
        service.schedule_followup = AsyncMock(return_value={
            "success": True,
            "followup_id": "followup_123"
        })
        service.get_pending_followups = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def followup_tools(self, mock_followup_service):
        """Instância das ferramentas de follow-up"""
        return FollowUpNauticoTools(mock_followup_service)

    @pytest.fixture
    def sample_lead_info(self):
        """Lead de exemplo"""
        return {
            "id": "12345",
            "name": "João Torcedor",
            "phone": "5581999999999"
        }

    @pytest.mark.asyncio
    async def test_schedule_nautico_followups(self, followup_tools, sample_lead_info, mock_followup_service):
        """Testa agendamento dos follow-ups do Náutico"""
        result = await followup_tools.schedule_nautico_followups(
            sample_lead_info,
            "5581999999999"
        )
        
        # Verificar resultado
        assert result["success"] is True
        assert result["total"] == 3
        assert len(result["scheduled_followups"]) == 3
        
        # Verificar que foram agendados follow-ups para 4h, 24h e 48h
        delays = [f["delay"] for f in result["scheduled_followups"]]
        assert "4h" in delays
        assert "24h" in delays
        assert "48h" in delays
        
        # Verificar que o follow-up de 48h tem ação de desqualificar
        followup_48h = next(f for f in result["scheduled_followups"] if f["delay"] == "48h")
        assert followup_48h["final"] is True
        assert followup_48h["action"] == "desqualificar_se_sem_resposta"
        
        # Verificar que o serviço foi chamado 3 vezes
        assert mock_followup_service.schedule_followup.call_count == 3

    @pytest.mark.asyncio
    async def test_process_final_followup_no_response(self, followup_tools, sample_lead_info):
        """Testa processamento do follow-up final sem resposta (desqualifica)"""
        with patch.object(followup_tools.stage_tools, 'move_to_desqualificado') as mock_desqualify:
            mock_desqualify.return_value = {"success": True, "stage": "desqualificado"}
            
            result = await followup_tools.process_final_followup_response(
                sample_lead_info, 
                has_response=False
            )
            
            assert result["success"] is True
            assert result["action"] == "desqualified"
            mock_desqualify.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_final_followup_with_response(self, followup_tools, sample_lead_info):
        """Testa processamento do follow-up final com resposta (continua)"""
        result = await followup_tools.process_final_followup_response(
            sample_lead_info,
            has_response=True
        )
        
        assert result["success"] is True
        assert result["action"] == "continue"

    def test_get_followup_template(self, followup_tools):
        """Testa templates de follow-up"""
        template_4h = followup_tools.get_followup_template("4h", "João")
        assert "João" in template_4h
        assert "dúvida" in template_4h
        
        template_48h = followup_tools.get_followup_template("48h", "Maria")
        assert "Maria" in template_48h
        assert "última tentativa" in template_48h

    def test_get_followup_schedule(self, followup_tools):
        """Testa cronograma de follow-ups"""
        schedule = followup_tools.get_followup_schedule()
        
        assert schedule["total_followups"] == 3
        assert schedule["max_duration"] == "48 horas"
        assert len(schedule["stages"]) == 3
        
        # Verificar estágios
        stages = schedule["stages"]
        assert stages[0]["delay"] == "4h"
        assert stages[1]["delay"] == "24h"
        assert stages[2]["delay"] == "48h"
        assert stages[2]["action_if_no_response"] == "desqualificar"


class TestIntegrationStageFollowup:
    """Testes de integração entre estágios e follow-ups"""

    @pytest.mark.asyncio
    async def test_complete_flow_novo_lead_to_qualificado(self):
        """Testa fluxo completo: Novo Lead → Em Qualificação → Qualificado"""
        # Mock dos serviços
        mock_crm = Mock()
        mock_crm.update_lead_stage = AsyncMock(return_value={"success": True})
        
        mock_followup = Mock()
        mock_followup.schedule_followup = AsyncMock(return_value={"success": True, "followup_id": "123"})
        
        # Ferramentas
        stage_tools = StageManagementTools(mock_crm)
        followup_tools = FollowUpNauticoTools(mock_followup)
        
        lead_info = {
            "id": "12345",
            "name": "João Torcedor",
            "phone": "5581999999999"
        }
        
        with patch('app.tools.stage_management_tools.supabase_client') as mock_supabase:
            mock_supabase.update_lead = AsyncMock()
            
            # 1. Mover para Em Qualificação
            result1 = await stage_tools.move_to_em_qualificacao(lead_info)
            assert result1["success"] is True
            
            # 2. Agendar follow-ups
            result2 = await followup_tools.schedule_nautico_followups(lead_info, "5581999999999")
            assert result2["success"] is True
            assert result2["total"] == 3
            
            # 3. Lead responde e paga - mover para Qualificado
            result3 = await stage_tools.move_to_qualificado(
                lead_info, 
                payment_value="39,90",
                payment_valid=True
            )
            assert result3["success"] is True
            assert result3["stage"] == "qualificado"

    @pytest.mark.asyncio
    async def test_complete_flow_no_response_desqualified(self):
        """Testa fluxo: Em Qualificação → Follow-ups → Sem resposta → Desqualificado"""
        # Mock dos serviços
        mock_crm = Mock()
        mock_crm.update_lead_stage = AsyncMock(return_value={"success": True})
        
        mock_followup = Mock()
        mock_followup.schedule_followup = AsyncMock(return_value={"success": True, "followup_id": "123"})
        
        # Ferramentas
        stage_tools = StageManagementTools(mock_crm)
        followup_tools = FollowUpNauticoTools(mock_followup)
        
        lead_info = {
            "id": "12345",
            "name": "João Torcedor",
            "phone": "5581999999999"
        }
        
        with patch('app.tools.stage_management_tools.supabase_client') as mock_supabase:
            mock_supabase.update_lead = AsyncMock()
            
            # 1. Mover para Em Qualificação
            result1 = await stage_tools.move_to_em_qualificacao(lead_info)
            assert result1["success"] is True
            
            # 2. Agendar follow-ups
            result2 = await followup_tools.schedule_nautico_followups(lead_info, "5581999999999")
            assert result2["success"] is True
            
            # 3. Processar follow-up final sem resposta (desqualifica automaticamente)
            with patch.object(followup_tools.stage_tools, 'move_to_desqualificado') as mock_desqualify:
                mock_desqualify.return_value = {"success": True, "stage": "desqualificado"}
                
                result3 = await followup_tools.process_final_followup_response(
                    lead_info, 
                    has_response=False
                )
                assert result3["success"] is True
                assert result3["action"] == "desqualified"
                mock_desqualify.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
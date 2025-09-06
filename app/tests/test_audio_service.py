"""
Testes para o AudioService - Envio de áudio inicial via Evolution API
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import base64
from app.services.audio_service import AudioService


class TestAudioService:
    """Testes para AudioService"""

    @pytest.fixture
    def audio_service(self):
        """Instância do AudioService para testes"""
        return AudioService()

    @pytest.fixture
    def sample_audio_content(self):
        """Conteúdo de áudio simulado"""
        return b"fake_audio_data_mp3_content_here"

    @pytest.fixture
    def sample_lead_info(self):
        """Lead de exemplo para testes"""
        return {
            "id": "12345",
            "name": "João Torcedor",
            "phone": "5581999999999"
        }

    @pytest.mark.asyncio
    async def test_download_and_convert_audio_success(self, audio_service, sample_audio_content):
        """Testa download e conversão de áudio para Base64"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = sample_audio_content
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(audio_service, '_get_session', return_value=mock_session):
            result = await audio_service._download_and_convert_audio("http://example.com/audio.mp3")
            
            # Verificar se o resultado é Base64 válido
            expected_base64 = base64.b64encode(sample_audio_content).decode('utf-8')
            assert result == expected_base64
            
            # Verificar se pode ser decodificado de volta
            decoded = base64.b64decode(result)
            assert decoded == sample_audio_content

    @pytest.mark.asyncio
    async def test_download_and_convert_audio_http_error(self, audio_service):
        """Testa erro HTTP ao baixar áudio"""
        mock_response = AsyncMock()
        mock_response.status = 404
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(audio_service, '_get_session', return_value=mock_session):
            with pytest.raises(Exception) as exc_info:
                await audio_service._download_and_convert_audio("http://example.com/notfound.mp3")
            
            assert "Erro HTTP 404" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_initial_audio_development_mode(self, audio_service, sample_lead_info):
        """Testa modo desenvolvimento (simulação)"""
        with patch('app.services.audio_service.settings') as mock_settings:
            mock_settings.environment = "development"
            mock_settings.debug = True
            
            result = await audio_service.send_initial_audio(
                "5581999999999", sample_lead_info
            )
            
            assert result["success"] is True
            assert result["simulated"] is True
            assert "desenvolvimento" in result["message"]

    @pytest.mark.asyncio
    async def test_send_initial_audio_success(self, audio_service, sample_lead_info, sample_audio_content):
        """Testa envio bem-sucedido de áudio inicial"""
        # Mock do download e conversão
        expected_base64 = base64.b64encode(sample_audio_content).decode('utf-8')
        
        with patch.object(audio_service, '_download_and_convert_audio', return_value=expected_base64):
            # Mock da resposta da Evolution API
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "key": {"id": "msg_12345"}
            }
            
            mock_session = AsyncMock()
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            with patch.object(audio_service, '_get_session', return_value=mock_session):
                with patch('app.services.audio_service.settings') as mock_settings:
                    mock_settings.environment = "production"
                    mock_settings.debug = False
                    
                    result = await audio_service.send_initial_audio(
                        "5581999999999", sample_lead_info
                    )
                    
                    assert result["success"] is True
                    assert result["phone_number"] == "555581999999999"
                    assert result["message_id"] == "msg_12345"
                    assert result["audio_url"] == audio_service.initial_audio_url

    @pytest.mark.asyncio
    async def test_send_initial_audio_api_error(self, audio_service, sample_lead_info, sample_audio_content):
        """Testa erro da API ao enviar áudio"""
        expected_base64 = base64.b64encode(sample_audio_content).decode('utf-8')
        
        with patch.object(audio_service, '_download_and_convert_audio', return_value=expected_base64):
            # Mock da resposta de erro da Evolution API
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text.return_value = "Internal Server Error"
            
            mock_session = AsyncMock()
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            with patch.object(audio_service, '_get_session', return_value=mock_session):
                with patch('app.services.audio_service.settings') as mock_settings:
                    mock_settings.environment = "production"
                    mock_settings.debug = False
                    
                    result = await audio_service.send_initial_audio(
                        "5581999999999", sample_lead_info
                    )
                    
                    assert result["success"] is False
                    assert "500" in result["message"]

    @pytest.mark.asyncio
    async def test_send_custom_audio_success(self, audio_service, sample_lead_info, sample_audio_content):
        """Testa envio de áudio customizado"""
        custom_url = "http://example.com/custom-audio.mp3"
        expected_base64 = base64.b64encode(sample_audio_content).decode('utf-8')
        
        with patch.object(audio_service, '_download_and_convert_audio', return_value=expected_base64):
            # Mock da resposta da Evolution API
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "key": {"id": "msg_custom_12345"}
            }
            
            mock_session = AsyncMock()
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            with patch.object(audio_service, '_get_session', return_value=mock_session):
                with patch('app.services.audio_service.settings') as mock_settings:
                    mock_settings.environment = "production"
                    mock_settings.debug = False
                    
                    result = await audio_service.send_custom_audio(
                        "5581999999999", custom_url, sample_lead_info
                    )
                    
                    assert result["success"] is True
                    assert result["phone_number"] == "555581999999999"
                    assert result["message_id"] == "msg_custom_12345"
                    assert result["audio_url"] == custom_url

    @pytest.mark.asyncio
    async def test_validate_audio_url_accessible(self, audio_service):
        """Testa validação de URL de áudio acessível"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {
            'content-type': 'audio/mpeg',
            'content-length': '1024'
        }
        
        mock_session = AsyncMock()
        mock_session.head.return_value.__aenter__.return_value = mock_response
        
        with patch.object(audio_service, '_get_session', return_value=mock_session):
            result = await audio_service.validate_audio_url("http://example.com/audio.mp3")
            
            assert result["success"] is True
            assert result["accessible"] is True
            assert result["content_type"] == "audio/mpeg"
            assert result["size"] == 1024

    @pytest.mark.asyncio
    async def test_validate_audio_url_not_accessible(self, audio_service):
        """Testa validação de URL de áudio não acessível"""
        mock_response = AsyncMock()
        mock_response.status = 404
        
        mock_session = AsyncMock()
        mock_session.head.return_value.__aenter__.return_value = mock_response
        
        with patch.object(audio_service, '_get_session', return_value=mock_session):
            result = await audio_service.validate_audio_url("http://example.com/notfound.mp3")
            
            assert result["success"] is False
            assert result["accessible"] is False
            assert "Erro HTTP 404" in result["message"]

    def test_phone_number_formatting(self, audio_service):
        """Testa formatação de números de telefone"""
        # Este teste verifica a lógica de formatação interna
        test_cases = [
            ("5581999999999", "555581999999999@s.whatsapp.net"),
            ("81999999999", "5581999999999@s.whatsapp.net"),
            ("+5581999999999", "555581999999999@s.whatsapp.net"),
            ("(81) 99999-9999", "5581999999999@s.whatsapp.net"),
        ]
        
        for input_phone, expected_whatsapp in test_cases:
            # Simular a lógica de limpeza
            clean_phone = ''.join(filter(str.isdigit, input_phone))
            if not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            whatsapp_number = f"{clean_phone}@s.whatsapp.net"
            
            assert whatsapp_number == expected_whatsapp

    @pytest.mark.asyncio
    async def test_initial_audio_url_constant(self, audio_service):
        """Testa se a URL do áudio inicial está correta"""
        expected_url = (
            "https://qvehtvvlalskxbeaflzs.supabase.co/storage/v1/object/public/"
            "documents/AUDIO-ENVIAR-NO-INICIO-DA-CONVERSA-2%20(1).mp3"
        )
        
        assert audio_service.initial_audio_url == expected_url


class TestAudioServiceIntegration:
    """Testes de integração do AudioService"""

    @pytest.mark.asyncio
    async def test_complete_audio_flow(self):
        """Testa fluxo completo: validação → download → conversão → envio"""
        audio_service = AudioService()
        sample_audio = b"fake_mp3_content"
        
        # Mock de todas as etapas
        with patch.object(audio_service, 'validate_audio_url') as mock_validate:
            mock_validate.return_value = {"success": True, "accessible": True}
            
            with patch.object(audio_service, '_download_and_convert_audio') as mock_download:
                expected_base64 = base64.b64encode(sample_audio).decode('utf-8')
                mock_download.return_value = expected_base64
                
                # Mock da Evolution API
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {"key": {"id": "msg_integration_test"}}
                
                mock_session = AsyncMock()
                mock_session.post.return_value.__aenter__.return_value = mock_response
                
                with patch.object(audio_service, '_get_session', return_value=mock_session):
                    with patch('app.services.audio_service.settings') as mock_settings:
                        mock_settings.environment = "production"
                        mock_settings.debug = False
                        
                        # Executar fluxo completo
                        result = await audio_service.send_initial_audio(
                            "5581999999999",
                            {"id": "test_lead", "name": "Test User"}
                        )
                        
                        # Verificar resultado
                        assert result["success"] is True
                        assert result["message_id"] == "msg_integration_test"
                        
                        # Verificar chamadas
                        mock_download.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
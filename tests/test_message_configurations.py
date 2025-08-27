"""Testes para validar configurações de mensagens do .env"""
import pytest
from app.config import settings
from app.services.message_splitter import MessageSplitter
from app.services.message_buffer import MessageBuffer


class TestMessageConfigurations:
    """Testa se as configurações de mensagens estão sendo aplicadas corretamente"""

    def test_message_max_length_configuration(self):
        """Testa se MESSAGE_MAX_LENGTH está configurado corretamente"""
        # Valor esperado do .env
        expected_max_length = 200
        
        # Verificar se a configuração está correta
        assert settings.message_max_length == expected_max_length
        
        # Verificar se MessageSplitter usa a configuração correta
        splitter = MessageSplitter(
            max_length=settings.message_max_length,
            add_indicators=settings.message_add_indicators,
            enable_smart_splitting=settings.enable_smart_splitting,
            smart_splitting_fallback=settings.smart_splitting_fallback
        )
        assert splitter.max_length == expected_max_length

    def test_message_buffer_timeout_configuration(self):
        """Testa se MESSAGE_BUFFER_TIMEOUT está configurado corretamente"""
        # Valor esperado do .env
        expected_timeout = 10.0
        
        # Verificar se a configuração está correta
        assert settings.message_buffer_timeout == expected_timeout
        
        # Verificar se MessageBuffer usa a configuração correta
        buffer = MessageBuffer(
            timeout=settings.message_buffer_timeout,
            max_size=10
        )
        assert buffer.timeout == expected_timeout

    def test_response_delay_configurations(self):
        """Testa se as configurações de RESPONSE_DELAY estão corretas"""
        # Valores esperados do .env
        expected_min = 1.5
        expected_max = 3.0
        expected_thinking = 5.0
        
        assert settings.response_delay_min == expected_min
        assert settings.response_delay_max == expected_max
        assert settings.response_delay_thinking == expected_thinking

    def test_typing_duration_configurations(self):
        """Testa se as configurações de TYPING_DURATION estão corretas"""
        # Valores esperados do .env
        expected_short = 2.0
        expected_medium = 3.5
        expected_long = 5.0
        
        assert settings.typing_duration_short == expected_short
        assert settings.typing_duration_medium == expected_medium
        assert settings.typing_duration_long == expected_long

    def test_message_splitter_configurations(self):
        """Testa se as configurações do MessageSplitter estão corretas"""
        # Verificar configurações booleanas
        assert settings.enable_message_splitter is True
        assert settings.enable_smart_splitting is True
        assert settings.smart_splitting_fallback is True
        assert settings.message_add_indicators is False
        
        # Verificar configurações numéricas
        assert settings.message_chunk_delay == 0.8

    def test_message_buffer_configurations(self):
        """Testa se as configurações do MessageBuffer estão corretas"""
        # Verificar se está habilitado
        assert settings.enable_message_buffer is True
        
        # Verificar timeout
        assert settings.message_buffer_timeout == 10.0

    def test_message_splitter_functionality(self):
        """Testa se o MessageSplitter funciona com as configurações corretas"""
        splitter = MessageSplitter(
            max_length=settings.message_max_length,
            add_indicators=settings.message_add_indicators,
            enable_smart_splitting=settings.enable_smart_splitting,
            smart_splitting_fallback=settings.smart_splitting_fallback
        )
        
        # Teste com mensagem longa
        long_message = "Esta é uma mensagem muito longa que deveria ser dividida em múltiplas partes quando exceder o limite máximo de caracteres configurado no arquivo .env que é de 200 caracteres para garantir que as mensagens sejam enviadas de forma adequada."
        
        chunks = splitter.split_message(long_message)
        
        # Verificar se foi dividida
        assert len(chunks) > 1
        
        # Verificar se cada chunk respeita o limite
        for chunk in chunks:
            assert len(chunk) <= settings.message_max_length

    def test_all_message_configurations_loaded(self):
        """Testa se todas as configurações de mensagens foram carregadas"""
        # Lista de todas as configurações de mensagens que devem existir
        required_configs = [
            'message_max_length',
            'message_buffer_timeout',
            'enable_message_buffer',
            'enable_message_splitter',
            'message_chunk_delay',
            'message_add_indicators',
            'enable_smart_splitting',
            'smart_splitting_fallback',
            'response_delay_min',
            'response_delay_max',
            'response_delay_thinking',
            'typing_duration_short',
            'typing_duration_medium',
            'typing_duration_long',
        ]
        
        # Verificar se todas as configurações existem
        for config in required_configs:
            assert hasattr(settings, config), f"Configuração {config} não encontrada"
            assert getattr(settings, config) is not None, f"Configuração {config} é None"

    def test_configuration_types(self):
        """Testa se os tipos das configurações estão corretos"""
        # Configurações numéricas
        assert isinstance(settings.message_max_length, int)
        assert isinstance(settings.message_buffer_timeout, float)
        assert isinstance(settings.message_chunk_delay, float)
        assert isinstance(settings.response_delay_min, float)
        assert isinstance(settings.response_delay_max, float)
        assert isinstance(settings.response_delay_thinking, float)
        assert isinstance(settings.typing_duration_short, float)
        assert isinstance(settings.typing_duration_medium, float)
        assert isinstance(settings.typing_duration_long, float)
        
        # Configurações booleanas
        assert isinstance(settings.enable_message_buffer, bool)
        assert isinstance(settings.enable_message_splitter, bool)
        assert isinstance(settings.message_add_indicators, bool)
        assert isinstance(settings.enable_smart_splitting, bool)
        assert isinstance(settings.smart_splitting_fallback, bool)

    def test_configuration_ranges(self):
        """Testa se os valores das configurações estão em ranges válidos"""
        # MESSAGE_MAX_LENGTH deve ser positivo e razoável
        assert 50 <= settings.message_max_length <= 4096
        
        # Timeouts devem ser positivos
        assert settings.message_buffer_timeout > 0
        assert settings.message_chunk_delay > 0
        
        # Response delays devem ser positivos e em ordem lógica
        assert settings.response_delay_min > 0
        assert settings.response_delay_max > settings.response_delay_min
        assert settings.response_delay_thinking > 0
        
        # Typing durations devem ser positivos e em ordem lógica
        assert settings.typing_duration_short > 0
        assert settings.typing_duration_medium > settings.typing_duration_short
        assert settings.typing_duration_long > settings.typing_duration_medium
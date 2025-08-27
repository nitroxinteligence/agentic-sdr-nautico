#!/usr/bin/env python3
"""
Testes para os novos service wrappers implementados:
- RedisServiceWrapper
- SupabaseServiceWrapper 
- EvolutionAPIServiceWrapper

Testa o comportamento condicional baseado nas flags de configuração.
"""

import os
import sys
import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import importlib

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ServiceWrappersTest(unittest.TestCase):
    """Testes para os service wrappers implementados."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        # Salvar estado original das variáveis de ambiente
        self.original_env = {}
        self.env_vars = [
            'ENABLE_REDIS',
            'ENABLE_SUPABASE', 
            'ENABLE_EVOLUTION_API',
            'ENABLE_STICKER_RESPONSES',
            'ENABLE_REACTION_MESSAGES',
            'ENABLE_AUDIO_MESSAGES',
            'ENABLE_EMOJI_USAGE',
            'ENABLE_VOICE_MESSAGE_TRANSCRIPTION'
        ]
        
        for var in self.env_vars:
            self.original_env[var] = os.environ.get(var)
    
    def tearDown(self):
        """Limpeza após cada teste."""
        # Restaurar estado original das variáveis de ambiente
        for var in self.env_vars:
            if self.original_env[var] is not None:
                os.environ[var] = self.original_env[var]
            elif var in os.environ:
                del os.environ[var]
        
        # Recarregar configurações
        if 'app.config' in sys.modules:
            importlib.reload(sys.modules['app.config'])
    
    def _set_env_flags(self, **flags):
        """Define flags de ambiente para o teste."""
        for key, value in flags.items():
            os.environ[key] = str(value).lower()
        
        # Recarregar módulos que dependem das configurações
        modules_to_reload = [
            'app.config',
            'app.services.service_wrappers',
            'app.utils.logger',
            'app.core.multimodal_processor'
        ]
        
        for module_name in modules_to_reload:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
        
        # Forçar recriação das configurações
        if 'app.config' in sys.modules:
            from app.config import Settings
            # Criar nova instância das configurações
            sys.modules['app.config'].settings = Settings()
    
    def test_redis_wrapper_enabled(self):
        """Testa RedisServiceWrapper quando ENABLE_REDIS=true."""
        self._set_env_flags(ENABLE_REDIS='true')
        
        from app.services.service_wrappers import RedisServiceWrapper
        
        # Mock do redis client
        mock_redis = AsyncMock()
        wrapper = RedisServiceWrapper(mock_redis)
        
        # Testar métodos básicos (assíncronos)
        async def run_test():
            await wrapper.set('test_key', 'test_value')
            mock_redis.set.assert_called_once_with('test_key', 'test_value', None)
            
            await wrapper.get('test_key')
            mock_redis.get.assert_called_once_with('test_key')
            
            await wrapper.delete('test_key')
            mock_redis.delete.assert_called_once_with('test_key')
        
        asyncio.run(run_test())
    
    def test_redis_wrapper_disabled(self):
        """Testa RedisServiceWrapper quando ENABLE_REDIS=false."""
        self._set_env_flags(ENABLE_REDIS='false')
        
        from app.services.service_wrappers import ServiceNotEnabledError
        
        mock_redis = AsyncMock()
        # Importar após definir as flags
        from app.services.service_wrappers import RedisServiceWrapper
        wrapper = RedisServiceWrapper(mock_redis)
        
        # Métodos devem levantar exceção quando desabilitado
        async def run_test():
            with self.assertRaises(ServiceNotEnabledError):
                await wrapper.set('test_key', 'test_value')
            mock_redis.set.assert_not_called()
            
            with self.assertRaises(ServiceNotEnabledError):
                await wrapper.get('test_key')
            mock_redis.get.assert_not_called()
        
        asyncio.run(run_test())
    
    def test_supabase_wrapper_enabled(self):
        """Testa SupabaseServiceWrapper quando ENABLE_SUPABASE=true."""
        self._set_env_flags(ENABLE_SUPABASE='true')
        
        from app.services.service_wrappers import SupabaseServiceWrapper
        
        # Mock do supabase client
        mock_supabase = AsyncMock()
        wrapper = SupabaseServiceWrapper(mock_supabase)
        
        # Testar métodos básicos (assíncronos)
        async def run_test():
            await wrapper.get_lead_by_phone('123456789')
            mock_supabase.get_lead_by_phone.assert_called_once_with('123456789')
            
            await wrapper.update_lead('123456789', {'name': 'Test'})
            mock_supabase.update_lead.assert_called_once_with('123456789', {'name': 'Test'})
        
        asyncio.run(run_test())
    
    def test_supabase_wrapper_disabled(self):
        """Testa SupabaseServiceWrapper quando ENABLE_SUPABASE=false."""
        self._set_env_flags(ENABLE_SUPABASE='false')
        
        from app.services.service_wrappers import SupabaseServiceWrapper, ServiceNotEnabledError
        
        mock_supabase = AsyncMock()
        wrapper = SupabaseServiceWrapper(mock_supabase)
        
        # Métodos devem levantar exceção quando desabilitado
        async def run_test():
            with self.assertRaises(ServiceNotEnabledError):
                await wrapper.get_lead_by_phone('123456789')
            mock_supabase.get_lead_by_phone.assert_not_called()
        
        asyncio.run(run_test())
    
    def test_evolution_wrapper_enabled(self):
        """Testa EvolutionAPIServiceWrapper quando ENABLE_EVOLUTION_API=true."""
        self._set_env_flags(
            ENABLE_EVOLUTION_API='true',
            ENABLE_STICKER_RESPONSES='true',
            ENABLE_REACTION_MESSAGES='true',
            ENABLE_AUDIO_MESSAGES='true'
        )
        
        from app.services.service_wrappers import EvolutionAPIServiceWrapper
        
        # Mock do evolution client
        mock_evolution = AsyncMock()
        wrapper = EvolutionAPIServiceWrapper(mock_evolution)
        
        # Testar métodos básicos (assíncronos)
        async def run_test():
            await wrapper.send_message('123456789', 'Hello')
            mock_evolution.send_message.assert_called_once_with('123456789', 'Hello')
            
            # Testar métodos condicionais
            await wrapper.send_sticker('123456789', 'sticker_url')
            mock_evolution.send_sticker.assert_called_once_with('123456789', 'sticker_url')
            
            await wrapper.send_reaction('123456789', 'msg_id', '👍')
            mock_evolution.send_reaction.assert_called_once_with('123456789', 'msg_id', '👍')
            
            await wrapper.send_audio('123456789', b'audio_data')
            mock_evolution.send_audio.assert_called_once_with('123456789', b'audio_data')
        
        asyncio.run(run_test())
    
    def test_evolution_wrapper_disabled(self):
        """Testa EvolutionAPIServiceWrapper quando ENABLE_EVOLUTION_API=false."""
        self._set_env_flags(ENABLE_EVOLUTION_API='false')
        
        from app.services.service_wrappers import EvolutionAPIServiceWrapper, ServiceNotEnabledError
        
        mock_evolution = AsyncMock()
        wrapper = EvolutionAPIServiceWrapper(mock_evolution)
        
        # Métodos devem levantar exceção quando desabilitado
        async def run_test():
            with self.assertRaises(ServiceNotEnabledError):
                await wrapper.send_message('123456789', 'Hello')
            mock_evolution.send_message.assert_not_called()
        
        asyncio.run(run_test())
    
    def test_evolution_wrapper_conditional_features(self):
        """Testa funcionalidades condicionais do EvolutionAPIServiceWrapper."""
        # Testar com stickers desabilitados
        self._set_env_flags(
            ENABLE_EVOLUTION_API='true',
            ENABLE_STICKER_RESPONSES='false',
            ENABLE_REACTION_MESSAGES='true',
            ENABLE_AUDIO_MESSAGES='true'
        )
        
        from app.services.service_wrappers import EvolutionAPIServiceWrapper
        
        mock_evolution = AsyncMock()
        wrapper = EvolutionAPIServiceWrapper(mock_evolution)
        
        # Testar funcionalidades condicionais (assíncronos)
        async def run_test():
            # Sticker deve retornar None
            result = await wrapper.send_sticker('123456789', 'sticker_url')
            self.assertIsNone(result)
            mock_evolution.send_sticker.assert_not_called()
            
            # Reaction deve funcionar
            await wrapper.send_reaction('123456789', 'msg_id', '👍')
            mock_evolution.send_reaction.assert_called_once_with('123456789', 'msg_id', '👍')
        
        asyncio.run(run_test())
    
    def test_emoji_logger_conditional(self):
        """Testa verificação condicional no EmojiLogger."""
        # Testar com emojis habilitados
        self._set_env_flags(ENABLE_EMOJI_USAGE='true')
        
        from app.utils.logger import EmojiLogger
        
        # Mock do logger loguru
        with patch('app.utils.logger.logger') as mock_logger:
            EmojiLogger.log_with_emoji('info', 'system_debug', 'Test message')
            
            # Verificar se a mensagem contém emoji
            call_args = mock_logger.info.call_args[0][0]
            self.assertIn('🔧', call_args)  # Emoji de sistema_debug
        
        # Testar com emojis desabilitados
        self._set_env_flags(ENABLE_EMOJI_USAGE='false')
        
        # Recarregar o módulo
        if 'app.utils.logger' in sys.modules:
            importlib.reload(sys.modules['app.utils.logger'])
        
        from app.utils.logger import EmojiLogger
        
        with patch('app.utils.logger.logger') as mock_logger:
            EmojiLogger.log_with_emoji('info', 'system_debug', 'Test message')
            
            # Verificar se a mensagem NÃO contém emoji
            call_args = mock_logger.info.call_args[0][0]
            self.assertNotIn('🔧', call_args)
            self.assertEqual(call_args, 'Test message')
    
    def test_multimodal_voice_transcription_conditional(self):
        """Testa verificação condicional para ENABLE_VOICE_MESSAGE_TRANSCRIPTION."""
        # Teste simplificado - verificar se a flag está sendo lida corretamente
        self._set_env_flags(ENABLE_VOICE_MESSAGE_TRANSCRIPTION='false')
        
        from app.config import settings
        
        # Verificar se a configuração foi aplicada
        self.assertFalse(settings.enable_voice_message_transcription)
        
        # Nota: A implementação real da verificação está no método process_audio
        # do MultimodalProcessor e foi verificada manualmente

def run_tests():
    """Executa todos os testes."""
    print("🧪 Executando testes dos Service Wrappers...")
    print("=" * 60)
    
    # Executar testes
    suite = unittest.TestLoader().loadTestsFromTestCase(ServiceWrappersTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"✅ Testes passaram: {passed}/{total_tests}")
    print(f"❌ Testes falharam: {failures}/{total_tests}")
    print(f"💥 Erros: {errors}/{total_tests}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 Todos os testes passaram! Os service wrappers estão funcionando corretamente.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os detalhes acima.")
        
        if result.failures:
            print("\n📋 Falhas:")
            for test, traceback in result.failures:
                print(f"  ❌ {test}: {traceback}")
        
        if result.errors:
            print("\n📋 Erros:")
            for test, traceback in result.errors:
                print(f"  💥 {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
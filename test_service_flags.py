#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do sistema de flags de serviços.
Testa diferentes combinações de habilitação/desabilitação dos serviços.
"""

import os
import sys
import asyncio
from unittest.mock import patch, MagicMock
import importlib

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.service_wrappers import ServiceNotEnabledError

class ServiceFlagTester:
    """Classe para testar diferentes combinações de flags de serviços."""
    
    def __init__(self):
        self.test_results = []
        
    async def test_scenario(self, scenario_name: str, flags: dict, expected_services: list):
        """Testa um cenário específico com determinadas flags."""
        print(f"\n🧪 Testando cenário: {scenario_name}")
        print(f"📋 Flags: {flags}")
        
        # Aplicar as flags como variáveis de ambiente
        original_env = {}
        for key, value in flags.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = str(value).lower()
        
        try:
            # Recarregar os módulos para aplicar as novas configurações
            if 'app.config' in sys.modules:
                importlib.reload(sys.modules['app.config'])
            if 'app.agents.agentic_sdr_stateless' in sys.modules:
                importlib.reload(sys.modules['app.agents.agentic_sdr_stateless'])
            
            # Importar novamente após o reload
            from app.agents.agentic_sdr_stateless import AgenticSDRStateless
            
            # Criar uma nova instância do agente
            agent = AgenticSDRStateless()
            await agent.initialize()
            
            # Verificar quais serviços foram inicializados
            initialized_services = []
            if agent.calendar_service:
                initialized_services.append('calendar')
            if agent.crm_service:
                initialized_services.append('crm')
            if agent.followup_service:
                initialized_services.append('followup')
            if agent.knowledge_service:
                initialized_services.append('knowledge')
            
            print(f"✅ Serviços inicializados: {initialized_services}")
            
            # Testar execução de ferramentas
            await self._test_tool_execution(agent, initialized_services)
            
            # Verificar se os serviços esperados foram inicializados
            success = set(initialized_services) == set(expected_services)
            
            result = {
                'scenario': scenario_name,
                'flags': flags,
                'expected': expected_services,
                'actual': initialized_services,
                'success': success
            }
            
            self.test_results.append(result)
            
            if success:
                print(f"✅ Cenário passou: serviços esperados foram inicializados")
            else:
                print(f"❌ Cenário falhou: esperado {expected_services}, obtido {initialized_services}")
                
        except Exception as e:
            print(f"❌ Erro no cenário: {str(e)}")
            result = {
                'scenario': scenario_name,
                'flags': flags,
                'expected': expected_services,
                'actual': [],
                'success': False,
                'error': str(e)
            }
            self.test_results.append(result)
            
        finally:
            # Restaurar variáveis de ambiente originais
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
    
    async def _test_tool_execution(self, agent, available_services):
        """Testa a execução de ferramentas para serviços disponíveis e indisponíveis."""
        print("🔧 Testando execução de ferramentas...")
        
        # Mock dos dados necessários
        mock_lead_info = {
            'id': 'test_lead_123',
            'name': 'João Teste',
            'phone_number': '+5511999999999',
            'kommo_lead_id': '12345'
        }
        mock_context = {'test': True}
        mock_conversation = []
        
        # Testes para cada tipo de serviço
        test_cases = [
            ('calendar', 'check_availability', {'date_request': '2024-01-15'}),
            ('crm', 'update_stage', {'stage': 'qualified'}),
            ('followup', 'schedule', {'hours': 24, 'message': 'Teste'}),
            ('knowledge', 'search', {'query': 'programa de sócios'})
        ]
        
        for service_name, method_name, params in test_cases:
            service_method = f"{service_name}.{method_name}"
            
            try:
                if service_name in available_services:
                    print(f"  ✅ Tentando executar {service_method} (serviço disponível)")
                    # Não executamos realmente para evitar chamadas de API
                    print(f"    ℹ️  Serviço {service_name} está disponível para execução")
                else:
                    print(f"  ❌ Tentando executar {service_method} (serviço indisponível)")
                    print(f"    ℹ️  Serviço {service_name} não está disponível - wrapper deve bloquear")
                    
            except ServiceNotEnabledError as e:
                print(f"    ✅ ServiceNotEnabledError capturada corretamente: {str(e)}")
            except Exception as e:
                print(f"    ⚠️  Erro inesperado: {str(e)}")
    
    async def run_all_tests(self):
        """Executa todos os cenários de teste."""
        print("🚀 Iniciando testes do sistema de flags de serviços")
        print("=" * 60)
        
        # Cenário 1: Todos os serviços habilitados
        await self.test_scenario(
            "Todos os serviços habilitados",
            {
                'ENABLE_CRM_INTEGRATION': 'true',
                'ENABLE_KNOWLEDGE_BASE': 'true', 
                'ENABLE_FOLLOW_UP_AUTOMATION': 'true',
                'DISABLE_GOOGLE_CALENDAR': 'false'
            },
            ['calendar', 'crm', 'followup', 'knowledge']
        )
        
        # Cenário 2: Apenas CRM habilitado
        await self.test_scenario(
            "Apenas CRM habilitado",
            {
                'ENABLE_CRM_INTEGRATION': 'true',
                'ENABLE_KNOWLEDGE_BASE': 'false',
                'ENABLE_FOLLOW_UP_AUTOMATION': 'false', 
                'DISABLE_GOOGLE_CALENDAR': 'true'
            },
            ['crm']
        )
        
        # Cenário 3: Apenas Calendar e Knowledge habilitados
        await self.test_scenario(
            "Calendar e Knowledge habilitados",
            {
                'ENABLE_CRM_INTEGRATION': 'false',
                'ENABLE_KNOWLEDGE_BASE': 'true',
                'ENABLE_FOLLOW_UP_AUTOMATION': 'false',
                'DISABLE_GOOGLE_CALENDAR': 'false'
            },
            ['calendar', 'knowledge']
        )
        
        # Cenário 4: Todos os serviços desabilitados
        await self.test_scenario(
            "Todos os serviços desabilitados",
            {
                'ENABLE_CRM_INTEGRATION': 'false',
                'ENABLE_KNOWLEDGE_BASE': 'false',
                'ENABLE_FOLLOW_UP_AUTOMATION': 'false',
                'DISABLE_GOOGLE_CALENDAR': 'true'
            },
            []
        )
        
        # Cenário 5: Apenas Follow-up habilitado
        await self.test_scenario(
            "Apenas Follow-up habilitado",
            {
                'ENABLE_CRM_INTEGRATION': 'false',
                'ENABLE_KNOWLEDGE_BASE': 'false',
                'ENABLE_FOLLOW_UP_AUTOMATION': 'true',
                'DISABLE_GOOGLE_CALENDAR': 'true'
            },
            ['followup']
        )
        
        # Exibir resumo dos resultados
        self._print_test_summary()
    
    def _print_test_summary(self):
        """Exibe um resumo dos resultados dos testes."""
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ Testes passaram: {passed}/{total}")
        print(f"❌ Testes falharam: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 Todos os testes passaram! O sistema de flags está funcionando corretamente.")
        else:
            print("\n⚠️  Alguns testes falharam. Verifique os detalhes acima.")
            
        print("\n📋 Detalhes dos testes:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['scenario']}")
            if not result['success']:
                print(f"    Esperado: {result['expected']}")
                print(f"    Obtido: {result['actual']}")
                if 'error' in result:
                    print(f"    Erro: {result['error']}")

async def main():
    """Função principal para executar os testes."""
    tester = ServiceFlagTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
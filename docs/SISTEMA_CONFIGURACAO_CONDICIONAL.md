# Sistema de Configuração Condicional

## Visão Geral

Este documento descreve o sistema de configuração condicional implementado no AgenticSDR, que permite habilitar/desabilitar serviços e funcionalidades através de flags no arquivo `.env`.

## Arquitetura

### 1. Configurações Centralizadas

Todas as configurações são gerenciadas através do arquivo `app/config.py` usando Pydantic Settings, que carrega automaticamente as variáveis do arquivo `.env`.

### 2. Service Wrappers

Implementamos wrappers condicionais em `app/services/service_wrappers.py` que:
- Verificam se o serviço está habilitado antes da execução
- Levantam `ServiceNotEnabledError` quando o serviço está desabilitado
- Encapsulam os serviços reais para adicionar verificações de habilitação

### 3. Integração no Agente Principal

O agente principal (`app/agents/agentic_sdr_stateless.py`) foi refatorado para:
- Instanciar serviços condicionalmente baseado nas flags
- Aplicar wrappers aos serviços habilitados
- Tratar erros de serviços desabilitados graciosamente

## Flags de Configuração Disponíveis

### Serviços Principais

| Flag | Descrição | Padrão | Serviço Afetado |
|------|-----------|--------|------------------|
| `ENABLE_CRM_INTEGRATION` | Habilita integração com Kommo CRM | `true` | CRMService |
| `ENABLE_KNOWLEDGE_BASE` | Habilita base de conhecimento | `true` | KnowledgeService |
| `ENABLE_FOLLOW_UP_AUTOMATION` | Habilita automação de follow-up | `true` | FollowUpService |
| `DISABLE_GOOGLE_CALENDAR` | Desabilita Google Calendar | `false` | CalendarService |
| `ENABLE_SUPABASE` | Habilita integração com Supabase | `true` | Supabase Client |
| `ENABLE_REDIS` | Habilita cache Redis | `true` | Redis Client |

### Funcionalidades Específicas

| Flag | Descrição | Padrão |
|------|-----------|--------|
| `ENABLE_CONTEXT_ANALYSIS` | Análise de contexto de conversas | `true` |
| `ENABLE_SENTIMENT_ANALYSIS` | Análise de sentimento | `true` |
| `ENABLE_MULTIMODAL_ANALYSIS` | Análise de mídia (imagens, áudio) | `true` |
| `ENABLE_MESSAGE_SPLITTER` | Divisão automática de mensagens | `true` |
| `ENABLE_TYPING_SIMULATION` | Simulação de digitação | `true` |

## Como Usar

### 1. Configuração no .env

```bash
# Desabilitar CRM
ENABLE_CRM_INTEGRATION=false

# Desabilitar Knowledge Base
ENABLE_KNOWLEDGE_BASE=false

# Habilitar Google Calendar (padrão é desabilitado)
DISABLE_GOOGLE_CALENDAR=false

# Desabilitar Follow-up
ENABLE_FOLLOW_UP_AUTOMATION=false
```

### 2. Verificação de Status

O sistema automaticamente:
- Não instancia serviços desabilitados
- Exibe logs informativos sobre serviços desabilitados
- Bloqueia execução de ferramentas de serviços desabilitados

### 3. Tratamento de Erros

Quando um serviço está desabilitado:
```python
try:
    await agent.calendar_service.check_availability()
except ServiceNotEnabledError as e:
    print(f"Serviço não disponível: {e}")
```

## Cenários de Uso

### Ambiente de Desenvolvimento
```bash
# Desabilitar integrações externas para desenvolvimento local
ENABLE_CRM_INTEGRATION=false
ENABLE_SUPABASE=false
DISABLE_GOOGLE_CALENDAR=true
ENABLE_REDIS=false
```

### Ambiente de Teste
```bash
# Habilitar apenas serviços essenciais para testes
ENABLE_CRM_INTEGRATION=true
ENABLE_KNOWLEDGE_BASE=true
ENABLE_FOLLOW_UP_AUTOMATION=false
DISABLE_GOOGLE_CALENDAR=true
```

### Ambiente de Produção
```bash
# Todos os serviços habilitados
ENABLE_CRM_INTEGRATION=true
ENABLE_KNOWLEDGE_BASE=true
ENABLE_FOLLOW_UP_AUTOMATION=true
DISABLE_GOOGLE_CALENDAR=false
ENABLE_SUPABASE=true
ENABLE_REDIS=true
```

## Implementação Técnica

### Service Wrappers

Cada wrapper implementa o padrão:

```python
class ServiceWrapper:
    def __init__(self, service_instance):
        self.service = service_instance
        self.enabled = service_instance is not None
    
    def _check_enabled(self):
        if not self.enabled:
            raise ServiceNotEnabledError("Serviço não habilitado")
    
    async def method(self, *args, **kwargs):
        self._check_enabled()
        return await self.service.method(*args, **kwargs)
```

### Inicialização Condicional

```python
# No construtor do agente
calendar_real = CalendarServiceReal() if not settings.disable_google_calendar else None
self.calendar_service = CalendarServiceWrapper(calendar_real) if calendar_real else None
```

## Logs e Monitoramento

O sistema gera logs informativos:

```
✅ Service: CRM Integration habilitado
ℹ️  Google Calendar desabilitado via configuração
❌ Knowledge Base não disponível - serviço desabilitado
```

## Testes

O arquivo `test_service_flags.py` contém testes automatizados que verificam:
- Inicialização correta de serviços baseada nas flags
- Bloqueio de execução para serviços desabilitados
- Funcionamento correto dos wrappers

### Executar Testes

```bash
python test_service_flags.py
```

## Benefícios

1. **Flexibilidade**: Configuração granular de funcionalidades
2. **Performance**: Não instancia serviços desnecessários
3. **Debugging**: Facilita isolamento de problemas
4. **Ambientes**: Configurações específicas por ambiente
5. **Manutenibilidade**: Código mais limpo e organizado

## Considerações de Escalabilidade

### Impacto na Escalabilidade
- **Redução de Overhead**: Serviços desabilitados não consomem recursos
- **Inicialização Mais Rápida**: Menos dependências para carregar
- **Menor Uso de Memória**: Apenas serviços necessários são instanciados
- **Rede Otimizada**: Conexões desnecessárias não são estabelecidas

### Facilidade de Manutenção
- **Configuração Centralizada**: Todas as flags em um local
- **Código Modular**: Wrappers isolam responsabilidades
- **Logs Claros**: Fácil identificação de serviços ativos/inativos
- **Testes Automatizados**: Validação contínua do sistema
- **Documentação Completa**: Guia claro de uso e configuração

### Próximos Passos Sugeridos
1. **Monitoramento**: Implementar métricas de uso por serviço
2. **Interface Admin**: Painel para alteração de flags em tempo real
3. **Configuração Dinâmica**: Recarregamento de configurações sem restart
4. **Alertas**: Notificações quando serviços críticos estão desabilitados
# Guia Rápido - Sistema de Configuração Condicional

## 🚀 Configurações Rápidas

### Desenvolvimento Local (Sem Integrações)
```bash
# Copie e cole no seu .env
ENABLE_CRM_INTEGRATION=false
ENABLE_SUPABASE=false
DISABLE_GOOGLE_CALENDAR=true
ENABLE_REDIS=false
ENABLE_FOLLOW_UP_AUTOMATION=false
ENABLE_KNOWLEDGE_BASE=false
```

### Teste de CRM Apenas
```bash
ENABLE_CRM_INTEGRATION=true
ENABLE_SUPABASE=true
DISABLE_GOOGLE_CALENDAR=true
ENABLE_REDIS=false
ENABLE_FOLLOW_UP_AUTOMATION=false
ENABLE_KNOWLEDGE_BASE=false
```

### Teste de Calendar Apenas
```bash
ENABLE_CRM_INTEGRATION=false
ENABLE_SUPABASE=true
DISABLE_GOOGLE_CALENDAR=false
ENABLE_REDIS=false
ENABLE_FOLLOW_UP_AUTOMATION=false
ENABLE_KNOWLEDGE_BASE=false
```

### Produção Completa
```bash
ENABLE_CRM_INTEGRATION=true
ENABLE_SUPABASE=true
DISABLE_GOOGLE_CALENDAR=false
ENABLE_REDIS=true
ENABLE_FOLLOW_UP_AUTOMATION=true
ENABLE_KNOWLEDGE_BASE=true
```

## 🔧 Flags Principais

| Flag | O que faz | Valores |
|------|-----------|----------|
| `ENABLE_CRM_INTEGRATION` | Liga/desliga Kommo CRM | `true`/`false` |
| `ENABLE_KNOWLEDGE_BASE` | Liga/desliga base de conhecimento | `true`/`false` |
| `ENABLE_FOLLOW_UP_AUTOMATION` | Liga/desliga follow-ups automáticos | `true`/`false` |
| `DISABLE_GOOGLE_CALENDAR` | Desliga Google Calendar | `true`/`false` |
| `ENABLE_SUPABASE` | Liga/desliga banco de dados | `true`/`false` |
| `ENABLE_REDIS` | Liga/desliga cache Redis | `true`/`false` |

## 🐛 Resolução de Problemas

### Erro: "ServiceNotEnabledError"
**Causa**: Tentativa de usar serviço desabilitado
**Solução**: Habilite o serviço no `.env` ou remova a funcionalidade

### Erro: Conexão com banco/API
**Causa**: Serviço habilitado mas sem credenciais
**Solução**: Configure as credenciais ou desabilite o serviço

### Logs: "serviço desabilitado via configuração"
**Causa**: Normal - serviço foi desabilitado intencionalmente
**Ação**: Nenhuma, a menos que você queira habilitar

## 📊 Verificar Status

### Executar Testes
```bash
python test_service_flags.py
```

### Verificar Logs
Procure por estas mensagens nos logs:
- ✅ `Service: [Nome] habilitado`
- ℹ️ `[Nome] desabilitado via configuração`
- ❌ `Erro: ServiceNotEnabledError`

## 🎯 Casos de Uso Comuns

### "Quero testar apenas o chat, sem integrações"
```bash
ENABLE_CRM_INTEGRATION=false
ENABLE_SUPABASE=false
DISABLE_GOOGLE_CALENDAR=true
ENABLE_REDIS=false
ENABLE_FOLLOW_UP_AUTOMATION=false
ENABLE_KNOWLEDGE_BASE=false
```

### "Quero testar agendamento de reuniões"
```bash
ENABLE_CRM_INTEGRATION=true
ENABLE_SUPABASE=true
DISABLE_GOOGLE_CALENDAR=false
ENABLE_REDIS=true
ENABLE_FOLLOW_UP_AUTOMATION=true
ENABLE_KNOWLEDGE_BASE=true
```

### "Problema no CRM, quero desabilitar temporariamente"
```bash
ENABLE_CRM_INTEGRATION=false
# Manter outras configurações
```

## ⚠️ Importante

1. **Reinicie o servidor** após alterar flags no `.env`
2. **Supabase é necessário** para a maioria das funcionalidades
3. **Redis melhora performance** mas não é obrigatório
4. **Teste sempre** após mudanças de configuração

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do sistema
2. Execute `python test_service_flags.py`
3. Consulte `docs/SISTEMA_CONFIGURACAO_CONDICIONAL.md` para detalhes técnicos
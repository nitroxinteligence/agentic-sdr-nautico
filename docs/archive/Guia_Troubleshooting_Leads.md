# 🔧 Guia de Troubleshooting - Sistema de Leads

## 📋 Índice
1. [Problemas Comuns](#problemas-comuns)
2. [Comandos de Diagnóstico](#comandos-de-diagnóstico)
3. [Análise de Logs](#análise-de-logs)
4. [Cenários de Teste](#cenários-de-teste)
5. [Soluções Rápidas](#soluções-rápidas)
6. [Escalação](#escalação)

---

## 🚨 Problemas Comuns

### 1. Leads com Nomes Genéricos

**Sintomas:**
- Leads aparecem como "Lead sem nome" ou "Usuário"
- pushName não está sendo extraído do webhook
- Nomes não são capturados em conversas

**Diagnóstico:**
```bash
# Verificar logs de CONTACTS_UPDATE
grep "CONTACTS_UPDATE" logs/app.log | tail -20

# Procurar por warnings específicos
grep "sem pushName ou telefone válido" logs/app.log | tail -10
```

**Possíveis Causas:**
- Estrutura de payload diferente do esperado
- Webhook não sendo recebido
- Falha na extração de pushName
- Lead já existe com nome válido

**Soluções:**
1. Verificar estrutura do payload recebido
2. Testar com script de debug: `python test_contacts_update_debug.py`
3. Verificar se o telefone está correto
4. Analisar logs de extração contextual

### 2. Falha na Extração Contextual

**Sintomas:**
- Nomes mencionados em conversas não são capturados
- Logs mostram "Nenhum nome foi extraído do texto"
- Padrões de nome não são reconhecidos

**Diagnóstico:**
```bash
# Verificar extração de nomes
grep "Nome extraído" logs/app.log | tail -10

# Procurar por warnings de extração
grep "Nenhum nome foi extraído" logs/app.log | tail -10
```

**Possíveis Causas:**
- Padrões de regex inadequados
- Texto com formatação especial
- Nome em formato não reconhecido
- Validação muito restritiva

**Soluções:**
1. Testar com script: `python test_real_scenarios.py`
2. Adicionar novos padrões de regex se necessário
3. Verificar validação de nomes
4. Analisar contexto da conversa

### 3. Webhook CONTACTS_UPDATE Não Processado

**Sintomas:**
- Nenhum log de CONTACTS_UPDATE
- Leads não são atualizados após mudança no WhatsApp
- Erro 500 no endpoint de webhook

**Diagnóstico:**
```bash
# Verificar se webhooks estão chegando
grep "POST /webhook" logs/access.log | tail -10

# Verificar erros no processamento
grep "ERROR.*webhook" logs/app.log | tail -10
```

**Possíveis Causas:**
- Configuração incorreta do webhook
- Erro na validação do payload
- Falha na conexão com banco de dados
- Estrutura de dados inesperada

**Soluções:**
1. Verificar configuração do webhook no WhatsApp Business API
2. Testar endpoint manualmente
3. Verificar conectividade com banco
4. Analisar payload recebido

---

## 🔍 Comandos de Diagnóstico

### Verificação Geral do Sistema
```bash
# Status geral dos logs
tail -50 logs/app.log

# Verificar erros recentes
grep "ERROR" logs/app.log | tail -20

# Verificar warnings recentes
grep "WARNING" logs/app.log | tail -20
```

### Análise de CONTACTS_UPDATE
```bash
# Todos os CONTACTS_UPDATE do dia
grep "$(date +%Y-%m-%d).*CONTACTS_UPDATE" logs/app.log

# CONTACTS_UPDATE com problemas
grep "CONTACTS_UPDATE sem pushName" logs/app.log | tail -10

# Sucessos na extração
grep "Lead encontrado para telefone" logs/app.log | tail -10
```

### Análise de Extração de Nomes
```bash
# Nomes extraídos com sucesso
grep "Nome extraído via" logs/app.log | tail -10

# Falhas na extração
grep "Nenhum nome foi extraído" logs/app.log | tail -10

# Validação de nomes
grep "Nome válido encontrado" logs/app.log | tail -10
```

### Monitoramento de Performance
```bash
# Tempo de processamento
grep "Processamento concluído" logs/app.log | tail -10

# Estatísticas de leads
grep "Lead atualizado" logs/app.log | wc -l

# Taxa de sucesso
grep "✅" logs/app.log | wc -l
```

---

## 📊 Análise de Logs

### Logs de Sucesso
```
✅ Lead encontrado para telefone +5511999887766: João Silva
✅ Nome extraído via padrão explícito: 'Maria Santos'
✅ pushName 'Pedro Costa' aplicado para lead ID 12345
✅ Lead atualizado com sucesso
```

### Logs de Warning
```
⚠️ CONTACTS_UPDATE sem pushName ou telefone válido. Phone: '', PushName: ''
⚠️ Lead não encontrado para telefone +5511888777666
⚠️ Nenhum nome foi extraído do texto
⚠️ pushName 'João' muito curto, não aplicado
```

### Logs de Erro
```
❌ Erro no processamento CONTACTS_UPDATE: KeyError 'phone'
❌ Falha na conexão com banco de dados
❌ Erro na validação do payload: campo obrigatório ausente
❌ Timeout na extração de contexto
```

### Interpretação dos Logs

#### Logs Normais (Esperados)
- `✅ Lead encontrado` - Sistema funcionando corretamente
- `⚠️ Lead não encontrado` - Normal para novos contatos
- `⚠️ pushName muito curto` - Validação funcionando

#### Logs Problemáticos
- `❌ Erro no processamento` - Requer investigação imediata
- `⚠️ sem pushName ou telefone válido` - Payload malformado
- Ausência de logs CONTACTS_UPDATE - Webhook não chegando

---

## 🧪 Cenários de Teste

### Teste Rápido de CONTACTS_UPDATE
```bash
# Executar teste básico
python test_contacts_update_debug.py

# Resultado esperado: 5/5 cenários passando
```

### Teste Completo do Sistema
```bash
# Executar todos os testes
python test_real_scenarios.py

# Resultado esperado: 8/8 cenários passando
```

### Teste Manual de Webhook
```bash
# Simular webhook CONTACTS_UPDATE
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CONTACTS_UPDATE",
    "data": {
      "phone": "+5511999887766",
      "pushName": "Teste Manual"
    }
  }'
```

### Teste de Extração Contextual
```python
# Script de teste rápido
from app.core.lead_manager import LeadManager

lead_manager = LeadManager()
messages = [{"role": "user", "content": "Oi, meu nome é João Silva"}]
result = lead_manager.extract_lead_info(messages)
print(f"Nome extraído: {result.get('name')}")
```

---

## ⚡ Soluções Rápidas

### 1. Reiniciar Processamento de Webhooks
```bash
# Reiniciar serviço
sudo systemctl restart webhook-service

# Verificar status
sudo systemctl status webhook-service
```

### 2. Limpar Cache de Leads
```python
# Script de limpeza
from app.core.lead_manager import LeadManager
lead_manager = LeadManager()
lead_manager.clear_cache()
```

### 3. Reprocessar Leads Sem Nome
```sql
-- Identificar leads sem nome
SELECT id, phone_number, name FROM leads 
WHERE name IS NULL OR name LIKE '%sem nome%';

-- Marcar para reprocessamento
UPDATE leads SET needs_reprocessing = true 
WHERE name IS NULL OR name LIKE '%sem nome%';
```

### 4. Verificar Configuração do Webhook
```bash
# Verificar URL do webhook
echo $WEBHOOK_URL

# Testar conectividade
curl -I $WEBHOOK_URL/health
```

---

## 📈 Métricas de Monitoramento

### KPIs Diários
```bash
# Taxa de sucesso CONTACTS_UPDATE
echo "Sucessos: $(grep 'Lead encontrado para telefone' logs/app.log | grep $(date +%Y-%m-%d) | wc -l)"
echo "Falhas: $(grep 'Lead não encontrado' logs/app.log | grep $(date +%Y-%m-%d) | wc -l)"

# Nomes extraídos
echo "Nomes extraídos: $(grep 'Nome extraído via' logs/app.log | grep $(date +%Y-%m-%d) | wc -l)"

# Erros críticos
echo "Erros: $(grep 'ERROR' logs/app.log | grep $(date +%Y-%m-%d) | wc -l)"
```

### Alertas Automáticos
```bash
# Script de monitoramento (executar a cada 5 minutos)
#!/bin/bash
ERRORS=$(grep "ERROR" logs/app.log | grep "$(date +%Y-%m-%d %H:%M)" | wc -l)
if [ $ERRORS -gt 5 ]; then
    echo "ALERTA: $ERRORS erros detectados no último minuto" | mail -s "Sistema Leads - Alerta" admin@empresa.com
fi
```

---

## 🆘 Escalação

### Nível 1 - Suporte Técnico
**Quando escalar:**
- Mais de 10 erros por hora
- Taxa de sucesso abaixo de 80%
- Webhooks não chegando por mais de 30 minutos

**Informações necessárias:**
- Logs dos últimos 30 minutos
- Resultado dos testes automatizados
- Métricas de performance

### Nível 2 - Desenvolvimento
**Quando escalar:**
- Erro sistemático não resolvido em 2 horas
- Necessidade de mudança no código
- Problema de arquitetura

**Informações necessárias:**
- Análise completa dos logs
- Reprodução do problema
- Impacto nos usuários

### Nível 3 - Arquitetura
**Quando escalar:**
- Problema de design do sistema
- Necessidade de refatoração
- Impacto em múltiplos componentes

---

## 📞 Contatos de Emergência

- **Suporte Técnico:** suporte@empresa.com
- **Desenvolvimento:** dev@empresa.com
- **Arquitetura:** arquitetura@empresa.com
- **Plantão 24h:** +55 11 9999-8888

---

## 📚 Recursos Adicionais

- **Documentação da API:** `/docs/api`
- **Dashboard de Métricas:** `/dashboard/leads`
- **Logs em Tempo Real:** `/logs/live`
- **Testes Automatizados:** `/tests/results`

---

*Última atualização: $(date +%Y-%m-%d)*
*Versão: 1.0*
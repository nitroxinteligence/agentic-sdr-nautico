# PRD: Correção da Extração de Telefone no Webhook CONTACTS_UPDATE

## 🎯 Problema Identificado

### Causa Raiz
O webhook `CONTACTS_UPDATE` da Evolution API envia o número de telefone no campo `remoteJid` (formato: `558182986181@s.whatsapp.net`), mas o código de extração de telefone em `webhooks.py` **NUNCA** tentava extrair deste campo específico.

### Evidências dos Logs
```json
{
  "remoteJid": "558182986181@s.whatsapp.net",
  "pushName": "Mateus M",
  "profilePicUrl": "...",
  "instanceId": "..."
}
```

### Tentativas de Extração Anteriores
O código tentava extrair telefone de:
- ✅ `id` (campo vazio no CONTACTS_UPDATE)
- ✅ `phone` (campo vazio no CONTACTS_UPDATE)
- ✅ `number` (campo vazio no CONTACTS_UPDATE)
- ✅ Estruturas aninhadas `contact.*`, `contactInfo.*`, `profile.*` (vazias)
- ❌ **`remoteJid` (NUNCA foi tentado - CAUSA RAIZ)**

## 🔧 Solução Implementada

### Alteração no Código
**Arquivo:** `app/api/webhooks.py`
**Linha:** ~240

```python
# ANTES: Começava direto com 'id'
# Tentativa 1: id direto
raw_id = contact_data.get('id', '')

# DEPOIS: Adicionada Tentativa 0 para remoteJid
# Tentativa 0: remoteJid (campo principal do CONTACTS_UPDATE)
raw_remote_jid = contact_data.get('remoteJid', '')
if raw_remote_jid:
    phone_number = raw_remote_jid.replace('@c.us', '').replace('@s.whatsapp.net', '')
    
# Tentativa 1: id direto (só se remoteJid falhou)
if not phone_number:
    raw_id = contact_data.get('id', '')
```

### Resultado do Teste
```
✅ Tentativa 0 - campo 'remoteJid' RAW: '558182986181@s.whatsapp.net'
✅ Tentativa 0 - telefone extraído de remoteJid: '558182986181'
✅ Telefone extraído: '558182986181' (válido: True)
✅ Nome do lead atualizado via CONTACTS_UPDATE: 558182986181 -> Mateus M
```

## 📊 Impacto

### Antes da Correção
- ❌ Webhook CONTACTS_UPDATE ignorado (telefone vazio)
- ❌ Leads não atualizados com pushName
- ❌ Perda de informações de contato

### Após a Correção
- ✅ Telefone extraído corretamente do remoteJid
- ✅ Leads atualizados com pushName via CONTACTS_UPDATE
- ✅ Sistema funcionando conforme esperado

## 🚀 Status

- [x] **Causa raiz identificada:** Campo `remoteJid` não era processado
- [x] **Solução implementada:** Adicionada Tentativa 0 para `remoteJid`
- [x] **Teste realizado:** Extração funcionando 100%
- [x] **Código corrigido:** `webhooks.py` atualizado
- [ ] **Deploy em produção:** Pendente

## 📝 Lições Aprendidas

1. **Análise de Payload:** Sempre verificar TODOS os campos disponíveis no payload
2. **Logging Detalhado:** Logs foram essenciais para identificar a causa raiz
3. **Testes Específicos:** Criar testes isolados para cada cenário de webhook
4. **Priorização de Campos:** `remoteJid` deve ser a primeira tentativa para CONTACTS_UPDATE

---

**Data:** 25/08/2025  
**Autor:** Assistente AI  
**Status:** ✅ RESOLVIDO
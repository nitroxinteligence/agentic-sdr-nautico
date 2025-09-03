# REDIS E FOLLOW-UP NÁUTICO - GUIA COMPLETO

## 🔍 PROBLEMA IDENTIFICADO

O sistema de follow-up do Náutico **não estava funcionando completamente** porque o Redis estava desabilitado no `docker-compose.yml`. O Redis é **ESSENCIAL** para o funcionamento dos follow-ups automáticos.

## ⚙️ COMO O SISTEMA DE FOLLOW-UP FUNCIONA

### 📊 ARQUITETURA COMPLETA:

```
1. [Marina Campelo] → Agenda follow-up via FollowUpServiceReal
                    ↓
2. [Supabase] → Salva follow-up com status "pending"
                    ↓  
3. [FollowUpSchedulerService] → Monitora Supabase a cada 15s
                    ↓
4. [Redis Queues] → Enfileira tarefas quando chegam na hora
                    ↓
5. [FollowUpWorker] → Consome filas e executa mensagens
                    ↓
6. [Evolution API] → Envia mensagens via WhatsApp
```

### 🚫 PROBLEMA ANTERIOR:
- **Redis desabilitado** → Etapas 4-6 não funcionavam
- Follow-ups ficavam **pendentes para sempre**
- Marina agendava, mas mensagens **nunca eram enviadas**

## ✅ SOLUÇÃO IMPLEMENTADA

### 1. **REDIS ATIVADO NO DOCKER-COMPOSE.YML**
```yaml
# Redis OBRIGATÓRIO para follow-ups do Náutico  
redis:
  image: redis:7-alpine
  container_name: sdr-redis-nautico
  restart: unless-stopped
  ports:
    - "6379:6379"
  networks:
    - sdr-network
  volumes:
    - redis-data:/data
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### 2. **WORKERS CRIADOS**
- **`start_workers.py`**: Script para iniciar os workers
- **`WorkerManager`**: Gerencia scheduler + worker
- **Handlers de sinal**: Para shutdown graceful

### 3. **SCRIPTS DE DEPLOY**
- **`docker-start.sh`**: Script completo de inicialização
- **Instruções claras** no main.py sobre workers

## 🚀 COMO USAR

### **OPÇÃO 1: Docker Compose (Recomendado)**
```bash
# 1. Iniciar sistema completo
chmod +x docker-start.sh
./docker-start.sh

# 2. Iniciar workers de follow-up (em terminal separado)
docker exec -it sdr-ia-solarprime python start_workers.py
```

### **OPÇÃO 2: Desenvolvimento Local**
```bash
# Terminal 1 - API Principal
python main.py

# Terminal 2 - Workers de Follow-up  
python start_workers.py
```

## 📋 FLUXO COMPLETO DOS FOLLOW-UPS NÁUTICO

### **ETAPA 1: AGENDAMENTO**
```python
# Marina Campelo agenda via prompt
await followup_service.schedule_followup(
    phone_number="5581999999999",
    message="Opa, João! Passando só pra saber se ficou alguma dúvida...",
    delay_hours=4,
    lead_info=lead_data
)
# → Salvo no Supabase com status "pending"
```

### **ETAPA 2: ENFILEIRAMENTO** 
```python
# FollowUpSchedulerService (roda a cada 15s)
# → Verifica Supabase por follow-ups na hora
# → Enfileira no Redis: "followup_tasks"
await redis.enqueue("followup_tasks", task_payload)
# → Atualiza status para "queued"
```

### **ETAPA 3: EXECUÇÃO**
```python
# FollowUpWorker consome fila do Redis
# → Usa AgenticSDR para gerar mensagem inteligente
# → Envia via Evolution API
# → Atualiza status para "executed"
```

## 🔄 PROTOCOLO ESPECÍFICO DO NÁUTICO

### **TIMING DOS FOLLOW-UPS:**
- **4 horas**: "Opa, [Nome]! Passando só pra saber se ficou alguma dúvida sobre o que a gente conversou..."
- **24 horas**: "E aí, tudo certo? Deu pra pensar na nossa conversa sobre fortalecer o Timão?"  
- **48 horas**: "Fala, [Nome]. Essa é minha última tentativa. Se ainda quiser fazer parte do nosso time de sócios, me chama aqui..."

### **LINGUAGEM AUTÊNTICA:**
- Tom pernambucano: "visse?", "massa", "arretado"
- Contexto alvirrubro: "Timão", "fortalecer o clube"
- Personalização baseada no histórico da conversa

## 🛡️ FUNCIONALIDADES DE SEGURANÇA

### **RATE LIMITING:**
- Máximo de follow-ups por lead por semana
- Locks distribuídos para evitar duplicação
- Timeout em operações Redis

### **MONITORAMENTO:**
- Logs detalhados de cada etapa
- Health checks do Redis
- Status tracking no Supabase

### **RECOVERY:**
- Auto-retry em falhas de rede
- Fallback graceful se Redis indisponível
- Status de failed para troubleshooting

## 📊 BENEFÍCIOS DA IMPLEMENTAÇÃO

### **ANTES (Redis Desabilitado):**
❌ Follow-ups agendados mas não enviados  
❌ Leads perdidos por falta de reengajamento  
❌ Marina "muda" após primeiro contato  

### **AGORA (Redis Ativo):**
✅ Follow-ups automáticos funcionais  
✅ Reengajamento inteligente de leads  
✅ Marina mantém conversas ativas  
✅ Maior taxa de conversão para sócios  

## 🔧 TROUBLESHOOTING

### **Redis não conecta:**
```bash
# Verificar status
docker-compose ps redis

# Ver logs
docker-compose logs redis

# Testar conexão
redis-cli -h localhost -p 6379 ping
```

### **Workers não processam:**
```bash
# Verificar filas
redis-cli -h localhost -p 6379
> LLEN queue:followup_tasks

# Restart workers
docker exec -it sdr-ia-nautico python start_workers.py
```

### **Follow-ups não enviados:**
```bash
# Verificar status no Supabase
SELECT * FROM follow_ups WHERE status = 'pending' ORDER BY created_at DESC;

# Forçar processamento
# No Redis: LPUSH queue:followup_tasks '{"task_type":"execute_followup",...}'
```

## 🎯 RESULTADO FINAL

**O sistema de follow-up do Náutico está 100% operacional!**

- ✅ Redis configurado e funcionando
- ✅ Workers processando filas
- ✅ Marina enviando follow-ups automaticamente  
- ✅ Protocolo específico do Náutico implementado
- ✅ Linguagem pernambucana autêntica
- ✅ Reengajamento inteligente de torcedores

**Agora os torcedores que responderem ao áudio do presidente vão receber follow-ups personalizados da Marina Campelo até se tornarem sócios do programa "Sócio Mais Fiel do Nordeste"!** ⚪🔴

---

**Vamos, Timbu! A Marina não desiste de nenhum torcedor alvirrubro!** 🏆
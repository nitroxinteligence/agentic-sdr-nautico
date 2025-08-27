✅ Usando variáveis de ambiente do servidor (EasyPanel)
2025-08-25 21:56:56.576 | INFO     | app.services.knowledge_service:__init__:24 | ✅ KnowledgeService inicializado (versão simplificada)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2025-08-25 21:56:56.600 | INFO     | app.utils.logger:log_with_emoji:75 | 🚀 Iniciando SDR IA Solar Prime v0.3
2025-08-25 21:56:56.605 | INFO     | app.integrations.redis_client:connect:35 | ✅ Conectado ao Redis: redis_redis:6379
2025-08-25 21:56:56.605 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Redis pronto | Data: {'data': {'url': 'redis_redis:6379'}}
2025-08-25 21:56:57.102 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Supabase pronto
2025-08-25 21:56:57.103 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Buffer Inteligente inicializado (timeout=15.0s, max=10)
2025-08-25 21:56:57.103 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Message Buffer pronto | Data: {'data': {'timeout': '15.0s'}}
2025-08-25 21:56:57.103 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Message Splitter inicializado (max=250, smart=ativada)
2025-08-25 21:56:57.103 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Message Splitter pronto | Data: {'data': {'max_length': 250}}
2025-08-25 21:56:57.112 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 ConversationMonitor inicializado pronto
2025-08-25 21:56:57.113 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ ✅ ConversationMonitor: Loop iniciado
2025-08-25 21:56:57.113 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Conversation Monitor pronto
2025-08-25 21:56:57.113 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Sistema Refatorado pronto | Data: {'data': {'modules': 'Core + Services'}}
2025-08-25 21:56:57.123 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ FollowUp Service pronto
2025-08-25 21:56:57.123 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 🔐 GoogleOAuthHandler inicializado
2025-08-25 21:56:57.134 | INFO     | app.services.knowledge_service:__init__:24 | ✅ KnowledgeService inicializado (versão simplificada)
2025-08-25 21:56:57.135 | INFO     | app.utils.logger:log_with_emoji:75 | 🚀 Iniciando AgenticSDR Stateless
2025-08-25 21:56:57.135 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-25 21:56:57.144 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo fallback OpenAI configurado pronto | Data: {'model': 'o3-mini'}
2025-08-25 21:56:57.144 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-25 21:56:57.145 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-25 21:56:57.145 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🎨 MultimodalProcessor habilitado pronto | Data: {'dependencies': {'ocr': True, 'audio': True, 'pdf': True}}
2025-08-25 21:56:57.145 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 LeadManager inicializado pronto
2025-08-25 21:56:57.145 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🧠 ContextAnalyzer inicializado pronto
2025-08-25 21:56:57.145 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 ConversationMonitor inicializado pronto
2025-08-25 21:56:57.146 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ ✅ ConversationMonitor: Loop iniciado
2025-08-25 21:56:57.337 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 🔄 Access token renovado com sucesso
2025-08-25 21:56:57.343 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: ✅ Serviço Google Calendar construído com OAuth
2025-08-25 21:56:57.997 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: Google Calendar conectado via OAuth ao calendário: 'leonardofvieira00@gmail.com' | Data: {'calendar_id': 'leonardofvieira00@gmail.com'}
2025-08-25 21:56:59.154 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Kommo CRM conectado: leonardofvieira00
2025-08-25 21:56:59.736 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 9 campos customizados mapeados
2025-08-25 21:57:00.241 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 30 variações de estágios mapeadas
2025-08-25 21:57:00.269 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Evolution API conectada: 1 instâncias
2025-08-25 21:57:00.270 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ AgenticSDR Stateless inicializado! pronto | Data: {'modules': ['ModelManager', 'MultimodalProcessor', 'LeadManager', 'ContextAnalyzer', 'CalendarService', 'CRMService', 'FollowUpService']}
2025-08-25 21:57:00.270 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ AgenticSDR (Stateless) pronto | Data: {'data': {'status': 'sistema pronto'}}
2025-08-25 21:57:00.270 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ FollowUp Services pronto
2025-08-25 21:57:00.270 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🔥 Pré-aquecendo AgenticSDR (Stateless)...
2025-08-25 21:57:00.280 | INFO     | app.services.knowledge_service:__init__:24 | ✅ KnowledgeService inicializado (versão simplificada)
2025-08-25 21:57:00.281 | INFO     | app.utils.logger:log_with_emoji:75 | 🚀 Iniciando AgenticSDR Stateless
2025-08-25 21:57:00.281 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-25 21:57:00.289 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo fallback OpenAI configurado pronto | Data: {'model': 'o3-mini'}
2025-08-25 21:57:00.290 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-25 21:57:00.290 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-25 21:57:00.290 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🎨 MultimodalProcessor habilitado pronto | Data: {'dependencies': {'ocr': True, 'audio': True, 'pdf': True}}
2025-08-25 21:57:00.290 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 LeadManager inicializado pronto
2025-08-25 21:57:00.290 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🧠 ContextAnalyzer inicializado pronto
2025-08-25 21:57:00.290 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 ConversationMonitor inicializado pronto
2025-08-25 21:57:00.291 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ ✅ ConversationMonitor: Loop iniciado
2025-08-25 21:57:00.293 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: ✅ Serviço Google Calendar construído com OAuth
2025-08-25 21:57:00.893 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: Google Calendar conectado via OAuth ao calendário: 'leonardofvieira00@gmail.com' | Data: {'calendar_id': 'leonardofvieira00@gmail.com'}
2025-08-25 21:57:01.656 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Kommo CRM conectado: leonardofvieira00
2025-08-25 21:57:02.225 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 9 campos customizados mapeados
⚠️ Rate Limiter: Usando burst para kommo
2025-08-25 21:57:02.941 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 30 variações de estágios mapeadas
2025-08-25 21:57:02.970 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Evolution API conectada: 1 instâncias
2025-08-25 21:57:02.970 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ AgenticSDR Stateless inicializado! pronto | Data: {'modules': ['ModelManager', 'MultimodalProcessor', 'LeadManager', 'ContextAnalyzer', 'CalendarService', 'CRMService', 'FollowUpService']}
2025-08-25 21:57:02.971 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ SDR IA Solar Prime pronto | Data: {'startup_ms': 6370.51}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:35830 - "GET /health HTTP/1.1" 200 OK
2025-08-25 21:57:09.613 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:52100 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:57:14.447 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:52100 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:57:14.502 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-25 21:57:14.503 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:761 | CHATS_UPDATE update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}, {'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution', 'date_time': '2025-08-25T18:57:14.477Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:52100 - "POST /webhook/evolution/chats-update HTTP/1.1" 200 OK
2025-08-25 21:57:14.511 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:52100 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:57:14.535 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:52100 - "POST /webhook/evolution/messages-upsert HTTP/1.1" 200 OK
2025-08-25 21:57:14.536 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Iniciando processamento de 1 nova(s) mensagem(ns)
2025-08-25 21:57:14.536 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Processando mensagem de 558182986181
2025-08-25 21:57:14.536 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Processando mídia. Message key: {'remoteJid': '558182986181@s.whatsapp.net', 'fromMe': False, 'id': '3A80DE420541622A5748', 'senderLid': '129472024072320@lid'}
2025-08-25 21:57:14.536 | WARNING  | app.utils.logger:log_with_emoji:75 | ⚠️ Nenhum tipo de mídia reconhecido encontrado no payload
2025-08-25 21:57:14.536 | INFO     | app.utils.logger:log_with_emoji:75 | 📥 Recebido text de 558182986181 | Data: {'preview': 'eu', 'sender': '558182986181', 'type': 'text'}
2025-08-25 21:57:14.738 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:57:14.739 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === INÍCIO ANÁLISE CONTACTS_UPDATE ===
2025-08-25 21:57:14.739 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Payload RAW completo:
{
  "event": "contacts.update",
  "instance": "SDR IA SolarPrime",
  "data": [
    {
      "remoteJid": "558182986181@s.whatsapp.net",
      "pushName": "Mateus M",
      "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
      "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
    }
  ],
  "destination": "https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution",
  "date_time": "2025-08-25T18:57:14.730Z",
  "sender": "558195554978@s.whatsapp.net",
  "server_url": "https://evoapi-evolution-api.fzvgou.easypanel.host",
  "apikey": "3ECB607589F3-4D35-949F-BA5D2D5892E9"
}
2025-08-25 21:57:14.739 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Tipo do payload: <class 'dict'>
2025-08-25 21:57:14.739 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Chaves do payload: ['event', 'instance', 'data', 'destination', 'date_time', 'sender', 'server_url', 'apikey']
2025-08-25 21:57:14.739 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ contact_data inicial: [
  {
    "remoteJid": "558182986181@s.whatsapp.net",
    "pushName": "Mateus M",
    "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
    "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
  }
]
2025-08-25 21:57:14.739 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ contact_data é lista com 1 itens
2025-08-25 21:57:14.740 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Usando primeiro item da lista: {
  "remoteJid": "558182986181@s.whatsapp.net",
  "pushName": "Mateus M",
  "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
  "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
}
2025-08-25 21:57:14.740 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ contact_data final para processamento: {
  "remoteJid": "558182986181@s.whatsapp.net",
  "pushName": "Mateus M",
  "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
  "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
}
2025-08-25 21:57:14.740 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Chaves disponíveis em contact_data: ['remoteJid', 'pushName', 'profilePicUrl', 'instanceId']
2025-08-25 21:57:14.740 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === INÍCIO EXTRAÇÃO DE TELEFONE ===
2025-08-25 21:57:14.740 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Tentativa 0 - campo 'remoteJid' RAW: '558182986181@s.whatsapp.net'
2025-08-25 21:57:14.741 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Tentativa 0 - telefone extraído de remoteJid: '558182986181'
2025-08-25 21:57:14.741 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === RESULTADO FINAL DA EXTRAÇÃO ===
2025-08-25 21:57:14.741 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Telefone extraído: '558182986181' (válido: True)
2025-08-25 21:57:14.742 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ PushName extraído: 'Mateus M' (válido: True)
2025-08-25 21:57:14.742 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === FIM ANÁLISE CONTACTS_UPDATE ===
2025-08-25 21:57:14.998 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Lead 558182986181 já possui nome 'Mateus M', não sobrescrevendo com 'Mateus M'
INFO:     10.11.0.4:52100 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:57:15.000 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:57:15.000 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 0.3s)
INFO:     10.11.0.4:35588 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:57:15.044 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-25 21:57:15.044 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:761 | CHATS_UPDATE update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution', 'date_time': '2025-08-25T18:57:15.034Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35588 - "POST /webhook/evolution/chats-update HTTP/1.1" 200 OK
2025-08-25 21:57:15.056 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:35588 - "POST /webhook/evolution/messages-upsert HTTP/1.1" 200 OK
2025-08-25 21:57:15.057 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Iniciando processamento de 1 nova(s) mensagem(ns)
2025-08-25 21:57:15.058 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Processando mensagem de 558182986181
2025-08-25 21:57:15.059 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Processando mídia. Message key: {'remoteJid': '558182986181@s.whatsapp.net', 'fromMe': False, 'id': '3A0A8DFF12B650FD8EF5', 'senderLid': '129472024072320@lid'}
2025-08-25 21:57:15.059 | WARNING  | app.utils.logger:log_with_emoji:75 | ⚠️ Nenhum tipo de mídia reconhecido encontrado no payload
2025-08-25 21:57:15.060 | INFO     | app.utils.logger:log_with_emoji:75 | 📥 Recebido text de 558182986181 | Data: {'preview': 'quero', 'sender': '558182986181', 'type': 'text'}
2025-08-25 21:57:15.063 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:35588 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:57:15.072 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-25 21:57:15.073 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:761 | CHATS_UPDATE update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558195554978@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution', 'date_time': '2025-08-25T18:57:15.056Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35588 - "POST /webhook/evolution/chats-update HTTP/1.1" 200 OK
2025-08-25 21:57:15.304 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:57:15.305 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 0.6s)
INFO:     10.11.0.4:35588 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:57:15.346 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:57:15.346 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 0.6s)
INFO:     10.11.0.4:35588 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:57:15.399 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:35588 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:57:16.062 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🔄 Processando 2 mensagens combinadas para 558182986181 (total: 8 chars)
2025-08-25 21:57:16.062 | INFO     | app.utils.logger:log_with_emoji:75 | 💬 🚀 INICIANDO PROCESSAMENTO PRINCIPAL - Telefone: 558182986181, Mensagem: 'eu
quero...', ID: 3A0A8DFF12B650FD8EF5
2025-08-25 21:57:17.506 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Lead encontrado - ID: 9c2bb788-7efc-408c-859f-07669786b765, Nome: 'Mateus M'
2025-08-25 21:57:17.507 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Conversa encontrada - ID: 25d7c06b-a1b0-4e38-b38c-0ed491591677
2025-08-25 21:57:17.507 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Conversa validada - ID: 25d7c06b-a1b0-4e38-b38c-0ed491591677, Phone: 558182986181
2025-08-25 21:57:18.945 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-25 21:57:18.945 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:761 | CHATS_UPDATE update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution', 'date_time': '2025-08-25T18:57:17.582Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35588 - "POST /webhook/evolution/chats-update HTTP/1.1" 200 OK
2025-08-25 21:57:18.946 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:52100 - "POST /webhook/evolution/messages-upsert HTTP/1.1" 200 OK
2025-08-25 21:57:18.946 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Iniciando processamento de 1 nova(s) mensagem(ns)
2025-08-25 21:57:18.947 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Processando mensagem de 558182986181
2025-08-25 21:57:18.947 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Processando mídia. Message key: {'remoteJid': '558182986181@s.whatsapp.net', 'fromMe': False, 'id': '3A7AFF9AFA065D6DBAAF', 'senderLid': '129472024072320@lid'}
2025-08-25 21:57:18.947 | WARNING  | app.utils.logger:log_with_emoji:75 | ⚠️ Nenhum tipo de mídia reconhecido encontrado no payload
2025-08-25 21:57:18.947 | INFO     | app.utils.logger:log_with_emoji:75 | 📥 Recebido text de 558182986181 | Data: {'preview': 'reagendar', 'sender': '558182986181', 'type': 'text'}
2025-08-25 21:57:18.948 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:57:18.948 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 4.2s)
INFO:     10.11.0.4:35600 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:57:18.949 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:57:18.950 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 4.2s)
INFO:     10.11.0.4:35602 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:57:18.951 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:35612 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:57:18.951 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Mensagem e cache salvos
2025-08-25 21:57:18.952 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Criando AGENTIC SDR Stateless...
2025-08-25 21:57:18.952 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ 🏭 Criando agente stateless com contexto...
2025-08-25 21:57:20.107 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Kommo CRM conectado: leonardofvieira00
2025-08-25 21:57:20.616 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-25 21:57:20.616 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:761 | CHATS_UPDATE update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution', 'date_time': '2025-08-25T18:57:20.609Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:35612 - "POST /webhook/evolution/chats-update HTTP/1.1" 200 OK
2025-08-25 21:57:20.653 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:35612 - "POST /webhook/evolution/messages-upsert HTTP/1.1" 200 OK
2025-08-25 21:57:20.654 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Iniciando processamento de 1 nova(s) mensagem(ns)
2025-08-25 21:57:20.654 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Processando mensagem de 558182986181
2025-08-25 21:57:20.654 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Processando mídia. Message key: {'remoteJid': '558182986181@s.whatsapp.net', 'fromMe': False, 'id': '3A3EAB812127AF2B9C35', 'senderLid': '129472024072320@lid'}
2025-08-25 21:57:20.655 | WARNING  | app.utils.logger:log_with_emoji:75 | ⚠️ Nenhum tipo de mídia reconhecido encontrado no payload
2025-08-25 21:57:20.655 | INFO     | app.utils.logger:log_with_emoji:75 | 📥 Recebido text de 558182986181 | Data: {'preview': 'já disse antes po', 'sender': '558182986181', 'type': 'text'}
2025-08-25 21:57:20.676 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 9 campos customizados mapeados
2025-08-25 21:57:20.877 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:57:20.877 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 6.1s)
INFO:     10.11.0.4:35612 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:57:20.938 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:57:20.938 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 6.2s)
INFO:     10.11.0.4:35612 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:57:21.249 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 30 variações de estágios mapeadas
2025-08-25 21:57:23.042 | INFO     | app.services.knowledge_service:__init__:24 | ✅ KnowledgeService inicializado (versão simplificada)
2025-08-25 21:57:23.043 | INFO     | app.utils.logger:log_with_emoji:75 | 🚀 Iniciando AgenticSDR Stateless
2025-08-25 21:57:23.043 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-25 21:57:23.053 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo fallback OpenAI configurado pronto | Data: {'model': 'o3-mini'}
2025-08-25 21:57:23.053 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-25 21:57:23.053 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-25 21:57:23.054 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🎨 MultimodalProcessor habilitado pronto | Data: {'dependencies': {'ocr': True, 'audio': True, 'pdf': True}}
2025-08-25 21:57:23.054 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 LeadManager inicializado pronto
2025-08-25 21:57:23.054 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🧠 ContextAnalyzer inicializado pronto
2025-08-25 21:57:23.054 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 ConversationMonitor inicializado pronto
2025-08-25 21:57:23.054 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ ✅ ConversationMonitor: Loop iniciado
2025-08-25 21:57:23.057 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: ✅ Serviço Google Calendar construído com OAuth
2025-08-25 21:57:23.341 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: Google Calendar conectado via OAuth ao calendário: 'leonardofvieira00@gmail.com' | Data: {'calendar_id': 'leonardofvieira00@gmail.com'}
2025-08-25 21:57:24.163 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Kommo CRM conectado: leonardofvieira00
⚠️ Rate Limiter: Usando burst para kommo
2025-08-25 21:57:24.703 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 9 campos customizados mapeados
⚠️ Rate Limiter: Usando burst para kommo
2025-08-25 21:57:25.210 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 30 variações de estágios mapeadas
2025-08-25 21:57:25.241 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Evolution API conectada: 1 instâncias
2025-08-25 21:57:25.241 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ AgenticSDR Stateless inicializado! pronto | Data: {'modules': ['ModelManager', 'MultimodalProcessor', 'LeadManager', 'ContextAnalyzer', 'CalendarService', 'CRMService', 'FollowUpService']}
2025-08-25 21:57:25.242 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ Agente stateless criado com contexto pronto | Data: {'history_count': 53, 'lead_name': 'Mateus M'}
2025-08-25 21:57:25.242 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ AGENTIC SDR Stateless pronto para uso
2025-08-25 21:57:25.242 | INFO     | app.utils.logger:log_with_emoji:75 | 🤖 AGENTIC SDR: 🤖 AGENTE STATELESS INICIADO - Mensagem: 'eu
quero...'
2025-08-25 21:57:25.243 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Mensagem do usuário registrada
2025-08-25 21:57:25.244 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Mensagem adicionada ao histórico. Total: 54 mensagens
2025-08-25 21:57:25.245 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Contexto analisado - Sentimento: {'enabled': True, 'sentiment': 'positivo', 'score': 0.2, 'confidence': 0.7}, Urgência: normal
2025-08-25 21:57:25.245 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Lead atualizado - Nome: 'Mateus M', Valor: 359.1
2025-08-25 21:57:25.246 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ CONTEXTO ATUALIZADO - Histórico e lead_info finalizados
2025-08-25 21:57:25.246 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Contexto atualizado - Lead: Mateus M, Histórico: 54 msgs
2025-08-25 21:57:25.246 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Sincronização externa concluída
2025-08-25 21:57:25.246 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ CRM Sync: Payload de atualização gerado. | Data: {'payload': {'chosen_flow': 'Compra com Desconto', 'name': 'Mateus M', 'bill_value': 359.1, 'phone': '558182986181', 'qualification_score': 35, 'tags': ['Compra com Desconto']}}
🚫 Rate Limiter: Bloqueando kommo. Aguarde 4.3s
⏳ Rate Limiter: Aguardando 5.3s para kommo...
⚠️ Rate Limiter: Usando burst para kommo
2025-08-25 21:57:30.845 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:48080 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:57:31.139 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ CRM Sync: Dados do lead atualizados no Kommo. | Data: {'payload': {'chosen_flow': 'Compra com Desconto', 'name': 'Mateus M', 'bill_value': 359.1, 'phone': '558182986181', 'qualification_score': 35, 'tags': ['Compra com Desconto']}}
2025-08-25 21:57:31.139 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Dados CRM sincronizados
INFO:     10.11.0.4:48080 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     127.0.0.1:59018 - "GET /health HTTP/1.1" 200 OK
2025-08-25 21:57:45.722 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta LLM gerada: '<RESPOSTA_FINAL>Recebido e anotado, Mateus! Essa sua determinação é o que faz o projeto dar certo. P...'
2025-08-25 21:57:45.723 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta do assistente registrada
2025-08-25 21:57:45.723 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ AGENTIC SUCCESS: ✅ AGENTE STATELESS CONCLUÍDO - 558182986181: 'eu
quero...' -> '<RESPOSTA_FINAL>Recebido e anotado, Mateus! Essa s...'
2025-08-25 21:57:45.724 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta gerada pelo agente: '<RESPOSTA_FINAL>Recebido e anotado, Mateus! Essa sua determinação é o que faz o projeto dar certo. P...'
2025-08-25 21:57:46.798 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta do assistente salva
2025-08-25 21:57:47.037 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Lead atualizado
2025-08-25 21:57:54.004 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Evolution API - Typing enviado para 558182986181 (duração: 4.73s, tamanho: 176)
2025-08-25 21:58:01.041 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Evolution API - Mensagem de texto enviada para 558182986181 (tamanho: 176, delay: 1.81s)
2025-08-25 21:58:01.041 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta enviada via WhatsApp
2025-08-25 21:58:01.041 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ PROCESSAMENTO PRINCIPAL CONCLUÍDO - 558182986181: 'eu
quero...' -> 'Recebido e anotado, Mateus! Essa sua determinação ...'
2025-08-25 21:58:02.191 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:57270 - "POST /webhook/evolution/messages-update HTTP/1.1" 200 OK
INFO:     127.0.0.1:48950 - "GET /health HTTP/1.1" 200 OK
2025-08-25 21:58:11.688 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:46624 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:58:14.004 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-25 21:58:14.005 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:761 | CHATS_UPDATE update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution', 'date_time': '2025-08-25T18:58:13.998Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:46624 - "POST /webhook/evolution/chats-update HTTP/1.1" 200 OK
2025-08-25 21:58:14.024 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:46624 - "POST /webhook/evolution/messages-upsert HTTP/1.1" 200 OK
2025-08-25 21:58:14.026 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Iniciando processamento de 1 nova(s) mensagem(ns)
2025-08-25 21:58:14.026 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Processando mensagem de 558182986181
2025-08-25 21:58:14.026 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Processando mídia. Message key: {'remoteJid': '558182986181@s.whatsapp.net', 'fromMe': False, 'id': '3ACA4F7A5DA120CBD757', 'senderLid': '129472024072320@lid'}
2025-08-25 21:58:14.026 | WARNING  | app.utils.logger:log_with_emoji:75 | ⚠️ Nenhum tipo de mídia reconhecido encontrado no payload
2025-08-25 21:58:14.027 | INFO     | app.utils.logger:log_with_emoji:75 | 📥 Recebido text de 558182986181 | Data: {'preview': 'reagende a reuniao', 'sender': '558182986181', 'type': 'text'}
2025-08-25 21:58:14.266 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:58:14.267 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === INÍCIO ANÁLISE CONTACTS_UPDATE ===
2025-08-25 21:58:14.267 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Payload RAW completo:
{
  "event": "contacts.update",
  "instance": "SDR IA SolarPrime",
  "data": [
    {
      "remoteJid": "558182986181@s.whatsapp.net",
      "pushName": "Mateus M",
      "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
      "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
    }
  ],
  "destination": "https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution",
  "date_time": "2025-08-25T18:58:14.259Z",
  "sender": "558195554978@s.whatsapp.net",
  "server_url": "https://evoapi-evolution-api.fzvgou.easypanel.host",
  "apikey": "3ECB607589F3-4D35-949F-BA5D2D5892E9"
}
2025-08-25 21:58:14.267 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Tipo do payload: <class 'dict'>
2025-08-25 21:58:14.268 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Chaves do payload: ['event', 'instance', 'data', 'destination', 'date_time', 'sender', 'server_url', 'apikey']
2025-08-25 21:58:14.268 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ contact_data inicial: [
  {
    "remoteJid": "558182986181@s.whatsapp.net",
    "pushName": "Mateus M",
    "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
    "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
  }
]
2025-08-25 21:58:14.268 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ contact_data é lista com 1 itens
2025-08-25 21:58:14.268 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Usando primeiro item da lista: {
  "remoteJid": "558182986181@s.whatsapp.net",
  "pushName": "Mateus M",
  "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
  "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
}
2025-08-25 21:58:14.269 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ contact_data final para processamento: {
  "remoteJid": "558182986181@s.whatsapp.net",
  "pushName": "Mateus M",
  "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
  "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
}
2025-08-25 21:58:14.269 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Chaves disponíveis em contact_data: ['remoteJid', 'pushName', 'profilePicUrl', 'instanceId']
2025-08-25 21:58:14.269 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === INÍCIO EXTRAÇÃO DE TELEFONE ===
2025-08-25 21:58:14.269 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Tentativa 0 - campo 'remoteJid' RAW: '558182986181@s.whatsapp.net'
2025-08-25 21:58:14.269 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Tentativa 0 - telefone extraído de remoteJid: '558182986181'
2025-08-25 21:58:14.269 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === RESULTADO FINAL DA EXTRAÇÃO ===
2025-08-25 21:58:14.269 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Telefone extraído: '558182986181' (válido: True)
2025-08-25 21:58:14.269 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ PushName extraído: 'Mateus M' (válido: True)
2025-08-25 21:58:14.270 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === FIM ANÁLISE CONTACTS_UPDATE ===
2025-08-25 21:58:14.543 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Lead 558182986181 já possui nome 'Mateus M', não sobrescrevendo com 'Mateus M'
INFO:     10.11.0.4:46624 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:58:14.544 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:58:14.544 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 0.3s)
INFO:     10.11.0.4:57468 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:58:15.030 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🔄 Processando 3 mensagens combinadas para 558182986181 (total: 46 chars)
2025-08-25 21:58:15.030 | INFO     | app.utils.logger:log_with_emoji:75 | 💬 🚀 INICIANDO PROCESSAMENTO PRINCIPAL - Telefone: 558182986181, Mensagem: 'reagendar
já disse antes po
reagende a reuniao...', ID: 3ACA4F7A5DA120CBD757
2025-08-25 21:58:15.718 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:57468 - "POST /webhook/evolution/messages-update HTTP/1.1" 200 OK
2025-08-25 21:58:15.719 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-25 21:58:15.719 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:765 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:46624 - "POST /webhook/evolution/chats-upsert HTTP/1.1" 200 OK
2025-08-25 21:58:15.720 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Lead encontrado - ID: 9c2bb788-7efc-408c-859f-07669786b765, Nome: 'Mateus M'
2025-08-25 21:58:15.720 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Conversa encontrada - ID: 25d7c06b-a1b0-4e38-b38c-0ed491591677
2025-08-25 21:58:15.720 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Conversa validada - ID: 25d7c06b-a1b0-4e38-b38c-0ed491591677, Phone: 558182986181
2025-08-25 21:58:16.428 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Mensagem e cache salvos
2025-08-25 21:58:16.429 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Criando AGENTIC SDR Stateless...
2025-08-25 21:58:16.429 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ 🏭 Criando agente stateless com contexto...
2025-08-25 21:58:17.192 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Kommo CRM conectado: leonardofvieira00
2025-08-25 21:58:17.764 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 9 campos customizados mapeados
2025-08-25 21:58:18.338 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 30 variações de estágios mapeadas
2025-08-25 21:58:19.782 | INFO     | app.services.knowledge_service:__init__:24 | ✅ KnowledgeService inicializado (versão simplificada)
2025-08-25 21:58:19.782 | INFO     | app.utils.logger:log_with_emoji:75 | 🚀 Iniciando AgenticSDR Stateless
2025-08-25 21:58:19.782 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-25 21:58:19.789 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo fallback OpenAI configurado pronto | Data: {'model': 'o3-mini'}
2025-08-25 21:58:19.790 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-25 21:58:19.790 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-25 21:58:19.790 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🎨 MultimodalProcessor habilitado pronto | Data: {'dependencies': {'ocr': True, 'audio': True, 'pdf': True}}
2025-08-25 21:58:19.792 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 LeadManager inicializado pronto
2025-08-25 21:58:19.792 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🧠 ContextAnalyzer inicializado pronto
2025-08-25 21:58:19.792 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 ConversationMonitor inicializado pronto
2025-08-25 21:58:19.793 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ ✅ ConversationMonitor: Loop iniciado
2025-08-25 21:58:19.795 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: ✅ Serviço Google Calendar construído com OAuth
2025-08-25 21:58:20.432 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: Google Calendar conectado via OAuth ao calendário: 'leonardofvieira00@gmail.com' | Data: {'calendar_id': 'leonardofvieira00@gmail.com'}
2025-08-25 21:58:21.742 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Kommo CRM conectado: leonardofvieira00
⚠️ Rate Limiter: Usando burst para kommo
2025-08-25 21:58:22.269 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 9 campos customizados mapeados
⚠️ Rate Limiter: Usando burst para kommo
2025-08-25 21:58:22.835 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 30 variações de estágios mapeadas
2025-08-25 21:58:22.859 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Evolution API conectada: 1 instâncias
2025-08-25 21:58:22.859 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ AgenticSDR Stateless inicializado! pronto | Data: {'modules': ['ModelManager', 'MultimodalProcessor', 'LeadManager', 'ContextAnalyzer', 'CalendarService', 'CRMService', 'FollowUpService']}
2025-08-25 21:58:22.860 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ Agente stateless criado com contexto pronto | Data: {'history_count': 55, 'lead_name': 'Mateus M'}
2025-08-25 21:58:22.860 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ AGENTIC SDR Stateless pronto para uso
2025-08-25 21:58:22.860 | INFO     | app.utils.logger:log_with_emoji:75 | 🤖 AGENTIC SDR: 🤖 AGENTE STATELESS INICIADO - Mensagem: 'reagendar
já disse antes po
reagende a reuniao...'
2025-08-25 21:58:22.861 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Mensagem do usuário registrada
2025-08-25 21:58:22.862 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Mensagem adicionada ao histórico. Total: 56 mensagens
2025-08-25 21:58:22.862 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Contexto analisado - Sentimento: {'enabled': True, 'sentiment': 'neutro', 'score': 0.0, 'confidence': 0.7}, Urgência: normal
2025-08-25 21:58:22.863 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Lead atualizado - Nome: 'Mateus M', Valor: 359.1
2025-08-25 21:58:22.863 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ CONTEXTO ATUALIZADO - Histórico e lead_info finalizados
2025-08-25 21:58:22.863 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Contexto atualizado - Lead: Mateus M, Histórico: 56 msgs
2025-08-25 21:58:22.863 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Sincronização externa concluída
2025-08-25 21:58:22.864 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ CRM Sync: Payload de atualização gerado. | Data: {'payload': {'chosen_flow': 'Compra com Desconto', 'name': 'Mateus M', 'bill_value': 359.1, 'phone': '558182986181', 'qualification_score': 35, 'tags': ['Compra com Desconto']}}
🚫 Rate Limiter: Bloqueando kommo. Aguarde 3.8s
⏳ Rate Limiter: Aguardando 4.8s para kommo...
2025-08-25 21:58:24.174 | ERROR    | app.utils.logger:log_with_emoji:75 | ❌ Erro Supabase: Erro ao buscar lead: Server disconnected | Data: {'table': 'leads'}
⚠️ Rate Limiter: Usando burst para kommo
INFO:     10.11.0.4:36326 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-25 21:58:28.375 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ CRM Sync: Dados do lead atualizados no Kommo. | Data: {'payload': {'chosen_flow': 'Compra com Desconto', 'name': 'Mateus M', 'bill_value': 359.1, 'phone': '558182986181', 'qualification_score': 35, 'tags': ['Compra com Desconto']}}
2025-08-25 21:58:28.375 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Dados CRM sincronizados
2025-08-25 21:58:36.402 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta LLM gerada: '<RESPOSTA_FINAL>Claro, Mateus. A gente reagenda sem problema nenhum. Para qual dia e horário você go...'
2025-08-25 21:58:36.404 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta do assistente registrada
2025-08-25 21:58:36.404 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ AGENTIC SUCCESS: ✅ AGENTE STATELESS CONCLUÍDO - 558182986181: 'reagendar
já disse antes po
reagende a reuniao...' -> '<RESPOSTA_FINAL>Claro, Mateus. A gente reagenda se...'
2025-08-25 21:58:36.404 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta gerada pelo agente: '<RESPOSTA_FINAL>Claro, Mateus. A gente reagenda sem problema nenhum. Para qual dia e horário você go...'
2025-08-25 21:58:37.884 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta do assistente salva
2025-08-25 21:58:38.124 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Lead atualizado
INFO:     127.0.0.1:60574 - "GET /health HTTP/1.1" 200 OK
2025-08-25 21:58:46.723 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Evolution API - Typing enviado para 558182986181 (duração: 3.39s, tamanho: 116)
2025-08-25 21:58:52.172 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Evolution API - Mensagem de texto enviada para 558182986181 (tamanho: 116, delay: 5.0s)
2025-08-25 21:58:52.173 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta enviada via WhatsApp
2025-08-25 21:58:52.174 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ PROCESSAMENTO PRINCIPAL CONCLUÍDO - 558182986181: 'reagendar
já disse antes po
reagende a reuniao...' -> 'Claro, Mateus. A gente reagenda sem problema nenhu...'
2025-08-25 21:58:53.066 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37200 - "POST /webhook/evolution/messages-update HTTP/1.1" 200 OK
2025-08-25 21:58:56.594 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37200 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:59:01.015 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-25 21:59:01.016 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:761 | CHATS_UPDATE update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution', 'date_time': '2025-08-25T18:59:01.006Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:37200 - "POST /webhook/evolution/chats-update HTTP/1.1" 200 OK
2025-08-25 21:59:01.040 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:37200 - "POST /webhook/evolution/messages-upsert HTTP/1.1" 200 OK
2025-08-25 21:59:01.041 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Iniciando processamento de 1 nova(s) mensagem(ns)
2025-08-25 21:59:01.041 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Processando mensagem de 558182986181
2025-08-25 21:59:01.042 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Processando mídia. Message key: {'remoteJid': '558182986181@s.whatsapp.net', 'fromMe': False, 'id': '3A3769C3FC66A9B4EFD7', 'senderLid': '129472024072320@lid'}
2025-08-25 21:59:01.042 | WARNING  | app.utils.logger:log_with_emoji:75 | ⚠️ Nenhum tipo de mídia reconhecido encontrado no payload
2025-08-25 21:59:01.042 | INFO     | app.utils.logger:log_with_emoji:75 | 📥 Recebido text de 558182986181 | Data: {'preview': 'para amanha as 10h por favor', 'sender': '558182986181', 'type': 'text'}
2025-08-25 21:59:01.272 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:59:01.272 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === INÍCIO ANÁLISE CONTACTS_UPDATE ===
2025-08-25 21:59:01.272 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Payload RAW completo:
{
  "event": "contacts.update",
  "instance": "SDR IA SolarPrime",
  "data": [
    {
      "remoteJid": "558182986181@s.whatsapp.net",
      "pushName": "Mateus M",
      "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
      "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
    }
  ],
  "destination": "https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution",
  "date_time": "2025-08-25T18:59:01.265Z",
  "sender": "558195554978@s.whatsapp.net",
  "server_url": "https://evoapi-evolution-api.fzvgou.easypanel.host",
  "apikey": "3ECB607589F3-4D35-949F-BA5D2D5892E9"
}
2025-08-25 21:59:01.272 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Tipo do payload: <class 'dict'>
2025-08-25 21:59:01.272 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Chaves do payload: ['event', 'instance', 'data', 'destination', 'date_time', 'sender', 'server_url', 'apikey']
2025-08-25 21:59:01.272 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ contact_data inicial: [
  {
    "remoteJid": "558182986181@s.whatsapp.net",
    "pushName": "Mateus M",
    "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
    "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
  }
]
2025-08-25 21:59:01.272 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ contact_data é lista com 1 itens
2025-08-25 21:59:01.273 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Usando primeiro item da lista: {
  "remoteJid": "558182986181@s.whatsapp.net",
  "pushName": "Mateus M",
  "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
  "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
}
2025-08-25 21:59:01.273 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ contact_data final para processamento: {
  "remoteJid": "558182986181@s.whatsapp.net",
  "pushName": "Mateus M",
  "profilePicUrl": "https://pps.whatsapp.net/v/t61.24694-24/521428372_23966156116410343_3058739794538851299_n.jpg?ccb=11-4&oh=01_Q5Aa2QHA0accMmwVQ0kGQqxZWoRDME2SU5PBaDhuJ4XQqsHBkw&oe=68BA0A4D&_nc_sid=5e03e0&_nc_cat=104",
  "instanceId": "02f1c146-f8b8-4f19-9e8a-d3517ee84269"
}
2025-08-25 21:59:01.273 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Chaves disponíveis em contact_data: ['remoteJid', 'pushName', 'profilePicUrl', 'instanceId']
2025-08-25 21:59:01.273 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === INÍCIO EXTRAÇÃO DE TELEFONE ===
2025-08-25 21:59:01.273 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Tentativa 0 - campo 'remoteJid' RAW: '558182986181@s.whatsapp.net'
2025-08-25 21:59:01.273 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Tentativa 0 - telefone extraído de remoteJid: '558182986181'
2025-08-25 21:59:01.273 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === RESULTADO FINAL DA EXTRAÇÃO ===
2025-08-25 21:59:01.274 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Telefone extraído: '558182986181' (válido: True)
2025-08-25 21:59:01.274 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ PushName extraído: 'Mateus M' (válido: True)
2025-08-25 21:59:01.274 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ === FIM ANÁLISE CONTACTS_UPDATE ===
2025-08-25 21:59:01.530 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Lead 558182986181 já possui nome 'Mateus M', não sobrescrevendo com 'Mateus M'
INFO:     10.11.0.4:37200 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:59:01.532 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:59:01.532 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 0.3s)
INFO:     10.11.0.4:37210 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:59:02.451 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37210 - "POST /webhook/evolution/messages-update HTTP/1.1" 200 OK
2025-08-25 21:59:02.451 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-upsert de evolution-api | Data: {'event': 'CHATS_UPSERT', 'endpoint': '/whatsapp/chats-upsert', 'source': 'evolution-api'}
2025-08-25 21:59:02.452 | WARNING  | app.api.webhooks:whatsapp_dynamic_webhook:765 | Evento não reconhecido: CHATS_UPSERT
INFO:     10.11.0.4:37200 - "POST /webhook/evolution/chats-upsert HTTP/1.1" 200 OK
2025-08-25 21:59:02.452 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🔄 Processando 1 mensagens combinadas para 558182986181 (total: 28 chars)
2025-08-25 21:59:02.453 | INFO     | app.utils.logger:log_with_emoji:75 | 💬 🚀 INICIANDO PROCESSAMENTO PRINCIPAL - Telefone: 558182986181, Mensagem: 'para amanha as 10h por favor...', ID: 3A3769C3FC66A9B4EFD7
2025-08-25 21:59:03.505 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37210 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:59:03.506 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Lead encontrado - ID: 9c2bb788-7efc-408c-859f-07669786b765, Nome: 'Mateus M'
2025-08-25 21:59:03.506 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Conversa encontrada - ID: 25d7c06b-a1b0-4e38-b38c-0ed491591677
2025-08-25 21:59:03.507 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Conversa validada - ID: 25d7c06b-a1b0-4e38-b38c-0ed491591677, Phone: 558182986181
2025-08-25 21:59:04.185 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-25 21:59:04.186 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:761 | CHATS_UPDATE update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution', 'date_time': '2025-08-25T18:59:04.104Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:37210 - "POST /webhook/evolution/chats-update HTTP/1.1" 200 OK
2025-08-25 21:59:04.187 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:37200 - "POST /webhook/evolution/messages-upsert HTTP/1.1" 200 OK
2025-08-25 21:59:04.187 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Iniciando processamento de 1 nova(s) mensagem(ns)
2025-08-25 21:59:04.187 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Processando mensagem de 558182986181
2025-08-25 21:59:04.188 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Processando mídia. Message key: {'remoteJid': '558182986181@s.whatsapp.net', 'fromMe': False, 'id': '3AC72DB9B9BA5DDEBFB0', 'senderLid': '129472024072320@lid'}
2025-08-25 21:59:04.188 | WARNING  | app.utils.logger:log_with_emoji:75 | ⚠️ Nenhum tipo de mídia reconhecido encontrado no payload
2025-08-25 21:59:04.188 | INFO     | app.utils.logger:log_with_emoji:75 | 📥 Recebido text de 558182986181 | Data: {'preview': 'ah nao', 'sender': '558182986181', 'type': 'text'}
2025-08-25 21:59:04.190 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Mensagem e cache salvos
2025-08-25 21:59:04.190 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Criando AGENTIC SDR Stateless...
2025-08-25 21:59:04.190 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ 🏭 Criando agente stateless com contexto...
2025-08-25 21:59:04.806 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:59:04.807 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 3.5s)
INFO:     10.11.0.4:37200 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:59:04.807 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/presence-update de evolution-api | Data: {'event': 'PRESENCE_UPDATE', 'endpoint': '/whatsapp/presence-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:37210 - "POST /webhook/evolution/presence-update HTTP/1.1" 200 OK
2025-08-25 21:59:04.808 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:59:04.809 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 3.5s)
INFO:     10.11.0.4:60246 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:59:05.410 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Kommo CRM conectado: leonardofvieira00
2025-08-25 21:59:06.825 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/chats-update de evolution-api | Data: {'event': 'CHATS_UPDATE', 'endpoint': '/whatsapp/chats-update', 'source': 'evolution-api'}
2025-08-25 21:59:06.825 | INFO     | app.api.webhooks:whatsapp_dynamic_webhook:761 | CHATS_UPDATE update recebido: {'event': 'chats.update', 'instance': 'SDR IA SolarPrime', 'data': [{'remoteJid': '558182986181@s.whatsapp.net', 'instanceId': '02f1c146-f8b8-4f19-9e8a-d3517ee84269'}], 'destination': 'https://sdr-api-evolution-api.fzvgou.easypanel.host/webhook/evolution', 'date_time': '2025-08-25T18:59:06.817Z', 'sender': '558195554978@s.whatsapp.net', 'server_url': 'https://evoapi-evolution-api.fzvgou.easypanel.host', 'apikey': '3ECB607589F3-4D35-949F-BA5D2D5892E9'}
INFO:     10.11.0.4:60246 - "POST /webhook/evolution/chats-update HTTP/1.1" 200 OK
2025-08-25 21:59:06.839 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-upsert de evolution-api | Data: {'event': 'MESSAGES_UPSERT', 'endpoint': '/whatsapp/messages-upsert', 'source': 'evolution-api'}
INFO:     10.11.0.4:60246 - "POST /webhook/evolution/messages-upsert HTTP/1.1" 200 OK
2025-08-25 21:59:06.840 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Iniciando processamento de 1 nova(s) mensagem(ns)
2025-08-25 21:59:06.840 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ Processando mensagem de 558182986181
2025-08-25 21:59:06.841 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Processando mídia. Message key: {'remoteJid': '558182986181@s.whatsapp.net', 'fromMe': False, 'id': '3A0E5546D7B7C3141E23', 'senderLid': '129472024072320@lid'}
2025-08-25 21:59:06.842 | WARNING  | app.utils.logger:log_with_emoji:75 | ⚠️ Nenhum tipo de mídia reconhecido encontrado no payload
2025-08-25 21:59:06.842 | INFO     | app.utils.logger:log_with_emoji:75 | 📥 Recebido text de 558182986181 | Data: {'preview': 'reagende para as 15h', 'sender': '558182986181', 'type': 'text'}
2025-08-25 21:59:07.075 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:59:07.076 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 5.8s)
INFO:     10.11.0.4:60246 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:59:07.115 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/contacts-update de evolution-api | Data: {'event': 'CONTACTS_UPDATE', 'endpoint': '/whatsapp/contacts-update', 'source': 'evolution-api'}
2025-08-25 21:59:07.115 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ 🚫 CONTACTS_UPDATE ignorado - Duplicata detectada para 558182986181@s.whatsapp.net (processado há 5.8s)
INFO:     10.11.0.4:60246 - "POST /webhook/evolution/contacts-update HTTP/1.1" 200 OK
2025-08-25 21:59:07.482 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 9 campos customizados mapeados
2025-08-25 21:59:08.094 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 30 variações de estágios mapeadas
INFO:     127.0.0.1:45236 - "GET /health HTTP/1.1" 200 OK
2025-08-25 21:59:09.530 | INFO     | app.services.knowledge_service:__init__:24 | ✅ KnowledgeService inicializado (versão simplificada)
2025-08-25 21:59:09.531 | INFO     | app.utils.logger:log_with_emoji:75 | 🚀 Iniciando AgenticSDR Stateless
2025-08-25 21:59:09.531 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo primário Gemini configurado pronto | Data: {'model': 'gemini-2.5-pro'}
2025-08-25 21:59:09.540 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo fallback OpenAI configurado pronto | Data: {'model': 'o3-mini'}
2025-08-25 21:59:09.540 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Modelo reasoning configurado pronto | Data: {'model': 'gemini-2.0-flash-thinking'}
2025-08-25 21:59:09.540 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Sistema de modelos configurado pronto | Data: {'primary_model': 'gemini-2.5-pro', 'fallback_available': True, 'reasoning_enabled': True}
2025-08-25 21:59:09.541 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🎨 MultimodalProcessor habilitado pronto | Data: {'dependencies': {'ocr': True, 'audio': True, 'pdf': True}}
2025-08-25 21:59:09.541 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 LeadManager inicializado pronto
2025-08-25 21:59:09.541 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 🧠 ContextAnalyzer inicializado pronto
2025-08-25 21:59:09.541 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ 📊 ConversationMonitor inicializado pronto
2025-08-25 21:59:09.542 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ ✅ ConversationMonitor: Loop iniciado
2025-08-25 21:59:09.544 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: ✅ Serviço Google Calendar construído com OAuth
2025-08-25 21:59:10.167 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: Google Calendar conectado via OAuth ao calendário: 'leonardofvieira00@gmail.com' | Data: {'calendar_id': 'leonardofvieira00@gmail.com'}
2025-08-25 21:59:10.926 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Kommo CRM conectado: leonardofvieira00
⚠️ Rate Limiter: Usando burst para kommo
2025-08-25 21:59:11.485 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 9 campos customizados mapeados
⚠️ Rate Limiter: Usando burst para kommo
2025-08-25 21:59:12.032 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Service: 📊 30 variações de estágios mapeadas
2025-08-25 21:59:12.066 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Service: ✅ Evolution API conectada: 1 instâncias
2025-08-25 21:59:12.067 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ AgenticSDR Stateless inicializado! pronto | Data: {'modules': ['ModelManager', 'MultimodalProcessor', 'LeadManager', 'ContextAnalyzer', 'CalendarService', 'CRMService', 'FollowUpService']}
2025-08-25 21:59:12.068 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ Agente stateless criado com contexto pronto | Data: {'history_count': 57, 'lead_name': 'Mateus M'}
2025-08-25 21:59:12.068 | INFO     | app.utils.logger:log_with_emoji:75 | ⚙️ AGENTIC SDR Stateless pronto para uso
2025-08-25 21:59:12.068 | INFO     | app.utils.logger:log_with_emoji:75 | 🤖 AGENTIC SDR: 🤖 AGENTE STATELESS INICIADO - Mensagem: 'para amanha as 10h por favor...'
2025-08-25 21:59:12.069 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Mensagem do usuário registrada
2025-08-25 21:59:12.069 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Mensagem adicionada ao histórico. Total: 58 mensagens
2025-08-25 21:59:12.070 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Contexto analisado - Sentimento: {'enabled': True, 'sentiment': 'neutro', 'score': 0.0, 'confidence': 0.7}, Urgência: normal
2025-08-25 21:59:12.071 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Lead atualizado - Nome: 'Mateus M', Valor: 359.1
2025-08-25 21:59:12.071 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ CONTEXTO ATUALIZADO - Histórico e lead_info finalizados
2025-08-25 21:59:12.071 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Contexto atualizado - Lead: Mateus M, Histórico: 58 msgs
2025-08-25 21:59:12.072 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Sincronização externa concluída
2025-08-25 21:59:12.072 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ CRM Sync: Payload de atualização gerado. | Data: {'payload': {'chosen_flow': 'Compra com Desconto', 'name': 'Mateus M', 'bill_value': 359.1, 'phone': '558182986181', 'qualification_score': 35, 'tags': ['Compra com Desconto']}}
🚫 Rate Limiter: Bloqueando kommo. Aguarde 2.7s
⏳ Rate Limiter: Aguardando 3.7s para kommo...
⚠️ Rate Limiter: Usando burst para kommo
INFO:     10.11.0.4:37302 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
2025-08-25 21:59:16.425 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ CRM Sync: Dados do lead atualizados no Kommo. | Data: {'payload': {'chosen_flow': 'Compra com Desconto', 'name': 'Mateus M', 'bill_value': 359.1, 'phone': '558182986181', 'qualification_score': 35, 'tags': ['Compra com Desconto']}}
2025-08-25 21:59:16.425 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Dados CRM sincronizados
2025-08-25 21:59:25.718 | INFO     | app.utils.logger:log_with_emoji:75 | 📅 Iniciando reagendamento para o lead: 9c2bb788-7efc-408c-859f-07669786b765
2025-08-25 21:59:25.966 | INFO     | app.utils.logger:log_with_emoji:75 | 📅 Reunião encontrada para reagendamento: fsb3omgv08pb24gks79sagj2i0
2025-08-25 21:59:26.192 | INFO     | app.utils.logger:log_with_emoji:75 | 📅 Verificando disponibilidade interna para 2025-08-26 10:00...
2025-08-25 21:59:26.394 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Horário 10:00 está livre.
2025-08-25 21:59:26.394 | INFO     | app.utils.logger:log_with_emoji:75 | 📅 Horário disponível. Atualizando evento fsb3omgv08pb24gks79sagj2i0...
2025-08-25 21:59:26.871 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Reunião fsb3omgv08pb24gks79sagj2i0 reagendada para 2025-08-26 às 10:00.
2025-08-25 21:59:27.464 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Qualificação 74bcb9ae-4e52-4841-88e2-898861d9a121 atualizada no Supabase.
2025-08-25 21:59:27.464 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ Tool executado: calendar.reschedule_meeting
2025-08-25 21:59:35.673 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Segunda chamada ao LLM bem-sucedida: <RESPOSTA_FINAL>Reunião reagendada com sucesso, Ma...
2025-08-25 21:59:35.674 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta LLM gerada: '<RESPOSTA_FINAL>Reunião reagendada com sucesso, Mateus! Ficou para amanhã, terça-feira, às 10h da ma...'
2025-08-25 21:59:35.675 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta do assistente registrada
2025-08-25 21:59:35.675 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ AGENTIC SUCCESS: ✅ AGENTE STATELESS CONCLUÍDO - 558182986181: 'para amanha as 10h por favor...' -> '<RESPOSTA_FINAL>Reunião reagendada com sucesso, Ma...'
2025-08-25 21:59:35.675 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta gerada pelo agente: '<RESPOSTA_FINAL>Reunião reagendada com sucesso, Mateus! Ficou para amanhã, terça-feira, às 10h da ma...'
2025-08-25 21:59:37.011 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta do assistente salva
2025-08-25 21:59:37.232 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Lead atualizado
INFO:     127.0.0.1:44228 - "GET /health HTTP/1.1" 200 OK
2025-08-25 21:59:48.068 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Evolution API - Typing enviado para 558182986181 (duração: 5.42s, tamanho: 222)
2025-08-25 21:59:56.992 | INFO     | app.utils.logger:log_with_emoji:75 | ℹ️ Evolution API - Mensagem de texto enviada para 558182986181 (tamanho: 222, delay: 5.0s)
2025-08-25 21:59:56.992 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ Resposta enviada via WhatsApp
2025-08-25 21:59:56.992 | INFO     | app.utils.logger:log_with_emoji:75 | ✅ ✅ PROCESSAMENTO PRINCIPAL CONCLUÍDO - 558182986181: 'para amanha as 10h por favor...' -> 'Reunião reagendada com sucesso, Mateus! Ficou para...'
2025-08-25 21:59:58.026 | INFO     | app.utils.logger:log_with_emoji:75 | 📞 Webhook recebido: /whatsapp/messages-update de evolution-api | Data: {'event': 'MESSAGES_UPDATE', 'endpoint': '/whatsapp/messages-update', 'source': 'evolution-api'}
INFO:     10.11.0.4:42732 - "POST /webhook/evolution/messages-update HTTP/1.1" 200 OK
INFO:     10.11.0.4:42732 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     10.11.0.4:42732 - "POST /webhook/kommo/events HTTP/1.1" 200 OK
INFO:     127.0.0.1:33616 - "GET /health HTTP/1.1" 200 OK
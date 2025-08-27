# Diagnóstico Definitivo: Falha de Sincronização de Estado no Handoff Humano

## 1. Resumo do Problema

O sistema continua a falhar em respeitar o protocolo de silêncio para leads em "Atendimento Humano". A investigação, baseada em logs de produção, revelou que a causa raiz não é um simples bug, mas uma **falha arquitetural fundamental** na forma como o sistema gerencia o estado do lead.

As correções anteriores, embora bem-intencionadas, trataram os sintomas. A solução definitiva requer uma mudança na arquitetura para garantir que o sistema opere com a fonte da verdade em tempo real.

## 2. Análise da Causa Raiz: A Fonte da Verdade Errada

O erro ocorre por uma razão fundamental: **o agente confia em dados locais que podem estar desatualizados.**

1.  **O Fluxo Falho:**
    *   Um vendedor move o Lead "Mateus" para o estágio "Atendimento Humano" diretamente na interface do Kommo CRM.
    *   O webhook do Kommo, que deveria notificar nosso sistema para ativar a pausa no Redis, falha ou não é processado a tempo.
    *   O Lead "Mateus" envia uma nova mensagem ("oi?") para o WhatsApp.
    *   Nosso webhook (`webhooks.py`) recebe a mensagem.
    *   Ele verifica a chave de pausa no Redis (`handoff:pause:5581...`). A chave **não existe**, pois o webhook do Kommo falhou.
    *   O sistema prossegue e cria uma instância do agente.
    *   Para construir o contexto, ele busca os dados do lead do **nosso banco de dados Supabase**. O Supabase ainda contém o estágio antigo do lead (ex: "Qualificado").
    *   O agente, operando com esta informação desatualizada, passa o contexto ao LLM.
    *   O LLM, corretamente, não vê a condição de "Atendimento Humano" e gera uma resposta de conversação normal, que é enviada ao lead.

**Conclusão:** A arquitetura atual é frágil porque depende de duas fontes de verdade (Supabase e Kommo) e assume uma sincronização perfeita via webhooks, o que não é garantido. A verdadeira fonte da verdade para o estágio do lead é o Kommo CRM, e o sistema precisa tratá-lo como tal.

## 3. A Solução Inteligente e Definitiva: Sincronização Ativa

A solução é parar de confiar cegamente nos dados locais e implementar uma camada de **sincronização ativa e em tempo real** no ponto mais crítico do fluxo: o recebimento da mensagem.

### 3.1. Arquitetura Proposta

A lógica será movida e centralizada em `create_agent_with_context` dentro de `app/api/webhooks.py`, que é o ponto onde todo o contexto é montado.

1.  **Modificar `create_agent_with_context`:**
    *   **Passo 1 - Obter Dados Locais:** Continuar buscando os dados do lead do Supabase como faz hoje. Isso nos dá o `lead_id` e outras informações de forma rápida.
    *   **Passo 2 - Sincronização em Tempo Real:** Se um `kommo_lead_id` existir nos dados do Supabase, o sistema **deve** fazer uma chamada em tempo real para a API do Kommo (`crm_service.get_lead_by_id(kommo_lead_id)`) para obter o estado mais recente do lead.
    *   **Passo 3 - Atualizar Estado Local:** Comparar o `status_id` (estágio) retornado pelo Kommo com o que está no Supabase. Se forem diferentes, atualizar o Supabase com o novo estágio.
    *   **Passo 4 - Ativar/Desativar Pausa (Lógica Centralizada):** Com o estágio mais recente e confiável em mãos (vindo do Kommo), verificar se ele corresponde ao `kommo_human_handoff_stage_id`.
        *   Se **sim**, chamar `redis_client.set_human_handoff_pause(phone)` e **lançar uma exceção especial** (ex: `HandoffActiveException`) para interromper a criação do agente imediatamente.
        *   Se **não**, chamar `redis_client.clear_human_handoff_pause(phone)` para garantir que a pausa seja removida caso o lead tenha voltado para o fluxo da IA.
    *   **Passo 5 - Tratamento da Exceção:** No bloco `try...except` que chama `create_agent_with_context`, capturar a `HandoffActiveException` e simplesmente encerrar o processamento da mensagem silenciosamente.

### 3.2. Vantagens Desta Arquitetura

-   **Fonte da Verdade Correta:** A decisão de pausar é sempre baseada no estado **em tempo real** do Kommo CRM, a única fonte de verdade confiável para o estágio do lead.
-   **Resiliência a Falhas de Webhook:** O sistema se torna auto-corretivo. Mesmo que o webhook do Kommo falhe, na próxima mensagem do cliente, o estado será sincronizado e a pausa será ativada corretamente.
-   **Eficiência:** A chamada extra à API do Kommo só ocorre quando um lead já conhecido envia uma mensagem, representando um custo mínimo para uma garantia de robustez máxima.
-   **Lógica Centralizada:** Toda a lógica de verificação e sincronização de handoff fica em um único lugar (`create_agent_with_context`), tornando o sistema mais limpo e fácil de manter, em vez de espalhado entre o agente, o webhook do Kommo e o webhook do WhatsApp.

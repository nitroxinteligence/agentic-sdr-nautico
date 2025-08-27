# Diagnóstico Final: Inconsistência de Esquema do Banco de Dados

## 1. Resumo do Problema

Após a implementação da sincronização ativa de estado, o sistema gera um erro de banco de dados (`PGRST204 - Could not find column`) ao tentar atualizar o estágio de um lead no Supabase.

Isso ocorre porque a nova lógica de sincronização no código (`app/api/webhooks.py`) introduziu a necessidade de um novo campo no banco de dados, mas o esquema do banco de dados não foi atualizado para refletir essa mudança.

## 2. Análise da Causa Raiz

A causa é uma **migração de banco de dados ausente**.

1.  **Código Modificado:** A função `create_agent_with_context` foi corretamente modificada para buscar o `status_id` mais recente do Kommo CRM.
2.  **Lógica de Sincronização:** Para manter a consistência, a linha `await supabase_client.update_lead(lead_data['id'], {'current_stage_id': current_status_id})` foi adicionada.
3.  **Esquema Desatualizado:** A tabela `leads` no Supabase não possui uma coluna chamada `current_stage_id`. Portanto, quando o `supabase_client` tenta executar a operação `UPDATE`, o PostgreSQL retorna um erro informando que a coluna não existe.

**Conclusão:** A lógica da aplicação está correta, mas o banco de dados no qual ela opera não está preparado para essa nova lógica.

## 3. A Solução Inteligente: Migração de Esquema

A solução é criar um script de migração SQL para adicionar a coluna ausente à tabela `leads`. Isso alinhará o esquema do banco de dados com os requisitos do código da aplicação.

### 3.1. Ação Proposta

1.  **Criar um novo arquivo de migração SQL:** `migrations/20250824_add_stage_id_to_leads.sql`.
2.  **Adicionar o seguinte comando SQL ao arquivo:**
    ```sql
    ALTER TABLE public.leads
    ADD COLUMN IF NOT EXISTS current_stage_id BIGINT;

    COMMENT ON COLUMN public.leads.current_stage_id IS 'Armazena o ID do estágio (status_id) mais recente sincronizado do Kommo CRM.';
    ```
3.  **Instruir o Usuário:** Informar sobre a necessidade de aplicar esta nova migração ao banco de dados Supabase para que a correção tenha efeito.

### 3.2. Vantagens da Solução

-   **Correção Definitiva:** Alinha permanentemente o banco de dados com a aplicação.
-   **Consistência de Dados:** Permite que o Supabase armazene o `status_id` mais recente, melhorando a capacidade de depuração e a consistência geral dos dados.
-   **Prática Padrão:** O uso de arquivos de migração é a abordagem padrão e correta para gerenciar a evolução de esquemas de banco de dados.

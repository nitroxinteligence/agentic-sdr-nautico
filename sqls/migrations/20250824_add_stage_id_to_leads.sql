-- Adiciona a coluna para armazenar o ID do estágio do Kommo CRM, permitindo uma sincronização de estado mais robusta.
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS current_stage_id BIGINT;

COMMENT ON COLUMN public.leads.current_stage_id IS 'Armazena o ID do estágio (status_id) mais recente sincronizado do Kommo CRM.';

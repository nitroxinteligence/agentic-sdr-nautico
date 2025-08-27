-- Adiciona o status 'queued' à constraint de verificação da tabela follow_ups.
-- Isso é necessário para que o FollowUpSchedulerService possa enfileirar tarefas
-- sem causar erros de banco de dados.

-- 1. Remove a constraint antiga
ALTER TABLE public.follow_ups
DROP CONSTRAINT follow_ups_status_check;

-- 2. Adiciona a nova constraint com o status 'queued'
ALTER TABLE public.follow_ups
ADD CONSTRAINT follow_ups_status_check 
CHECK (status::text = ANY (ARRAY[
    'pending'::character varying,
    'executed'::character varying,
    'failed'::character varying,
    'cancelled'::character varying,
    'queued'::character varying
]::text[]));

-- 3. (Opcional) Comente a linha abaixo se não quiser ver a confirmação
SELECT 'Constraint follow_ups_status_check atualizada com sucesso para incluir o status queued.';

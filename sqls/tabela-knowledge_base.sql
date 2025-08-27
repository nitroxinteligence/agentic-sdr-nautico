create table public.knowledge_base (
  id uuid not null default gen_random_uuid (),
  category character varying(100) not null,
  question text not null,
  answer text not null,
  keywords text[] null,
  metadata jsonb null default '{}'::jsonb,
  embedding public.vector null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  constraint knowledge_base_pkey primary key (id)
) TABLESPACE pg_default;

create index IF not exists idx_knowledge_category on public.knowledge_base using btree (category) TABLESPACE pg_default;

create index IF not exists idx_knowledge_keywords on public.knowledge_base using gin (keywords) TABLESPACE pg_default;

create index IF not exists idx_knowledge_embedding on public.knowledge_base using ivfflat (embedding vector_cosine_ops) TABLESPACE pg_default;

create index IF not exists idx_knowledge_base_question_gin on public.knowledge_base using gin (to_tsvector('portuguese'::regconfig, question)) TABLESPACE pg_default;

create index IF not exists idx_knowledge_base_answer_gin on public.knowledge_base using gin (to_tsvector('portuguese'::regconfig, answer)) TABLESPACE pg_default;

create trigger update_knowledge_base_updated_at BEFORE
update on knowledge_base for EACH row
execute FUNCTION update_updated_at_column ();
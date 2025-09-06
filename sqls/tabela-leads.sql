create table public.leads (
  id uuid not null default extensions.uuid_generate_v4 (),
  phone_number character varying(50) not null,
  name character varying(100) null,
  email character varying(100) null,
  membership_interest integer null,
  current_stage character varying(50) null default 'INITIAL_CONTACT'::character varying,
  qualification_score integer null,
  interested boolean null default true,
  kommo_lead_id character varying(50) null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  updated_at timestamp with time zone null default CURRENT_TIMESTAMP,
  qualification_status character varying(20) null default 'PENDING'::character varying,
  last_interaction timestamp with time zone null default now(),
  chosen_flow character varying(100) null,
  google_event_link text null,
  preferences jsonb null default '{}'::jsonb,
  total_messages integer null default 0,
  interaction_count integer null default 0,
  processed_message_count integer null default 0,
  chosen_membership_plan text null,
  membership_interest_level text null,
  location text null,
  conversation_id text null,
  solution_type text null,
  bill_value decimal(10,2) null,
  calendar_link text null,
  stage_id text null,
  stage_name text null default 'Novo Lead',
  last_interaction_at timestamp with time zone null,
  notes text null,
  initial_audio_sent boolean null default false,
  payment_value decimal(10,2) null,
  payer_name text null,
  is_valid_nautico_payment boolean null default false,
  ai_paused boolean null default false,
  property_type text null,
  interests jsonb null default '[]'::jsonb,
  objections jsonb null default '[]'::jsonb,
  phone text null,
  constraint leads_pkey primary key (id),
  constraint leads_phone_number_key unique (phone_number),
  constraint leads_chosen_flow_check check (
    (
      (chosen_flow is null)
      or (
        (chosen_flow)::text = any (
          (
            array[
              'Sócio Contribuinte'::character varying,
              'Sócio Patrimonial'::character varying,
              'Sócio Remido'::character varying,
              'Sócio Benemérito'::character varying
            ]
          )::text[]
        )
      )
    )
  ),
  constraint leads_qualification_score_check check (
    (
      (qualification_score >= 0)
      and (qualification_score <= 100)
    )
  ),
  constraint leads_qualification_status_check check (
    (
      (qualification_status)::text = any (
        (
          array[
            'PENDING'::character varying,
            'QUALIFIED'::character varying,
            'NOT_QUALIFIED'::character varying
          ]
        )::text[]
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_leads_stage on public.leads using btree (current_stage) TABLESPACE pg_default;

create index IF not exists idx_leads_interested on public.leads using btree (interested) TABLESPACE pg_default;

create index IF not exists idx_leads_created on public.leads using btree (created_at desc) TABLESPACE pg_default;

create index IF not exists idx_leads_phone on public.leads using btree (phone_number) TABLESPACE pg_default;

create index IF not exists idx_leads_qualification_status on public.leads using btree (qualification_status) TABLESPACE pg_default;

create index IF not exists idx_leads_created_brin on public.leads using brin (created_at) TABLESPACE pg_default;

create index IF not exists idx_leads_status_qualified on public.leads using btree (qualification_status, qualification_score) TABLESPACE pg_default
where
  ((qualification_status)::text = 'QUALIFIED'::text);

create index IF not exists idx_leads_chosen_flow on public.leads using btree (chosen_flow) TABLESPACE pg_default
where
  (chosen_flow is not null);

create index IF not exists idx_leads_google_event_link on public.leads using btree (google_event_link) TABLESPACE pg_default
where
  (google_event_link is not null);

create index IF not exists idx_leads_preferences on public.leads using gin (preferences) TABLESPACE pg_default;

create index IF not exists idx_leads_total_messages on public.leads using btree (total_messages) TABLESPACE pg_default;

create index IF not exists idx_leads_interaction_count on public.leads using btree (interaction_count) TABLESPACE pg_default;

create index IF not exists idx_leads_email on public.leads using btree (email) TABLESPACE pg_default
where
  (email is not null);

create index IF not exists idx_leads_updated on public.leads using btree (updated_at) TABLESPACE pg_default;

create index IF not exists idx_leads_qualification_status_new on public.leads using btree (qualification_status) TABLESPACE pg_default;

create index IF not exists idx_leads_membership_interest on public.leads using btree (membership_interest) TABLESPACE pg_default
where
  (membership_interest > 0);

create index IF not exists idx_leads_stage_id on public.leads using btree (stage_id) TABLESPACE pg_default;

create index IF not exists idx_leads_stage_name on public.leads using btree (stage_name) TABLESPACE pg_default;

create index IF not exists idx_leads_kommo_lead_id on public.leads using btree (kommo_lead_id) TABLESPACE pg_default;

create index IF not exists idx_leads_location on public.leads using btree (location) TABLESPACE pg_default
where
  (location is not null);

create index IF not exists idx_leads_conversation_id on public.leads using btree (conversation_id) TABLESPACE pg_default
where
  (conversation_id is not null);

create index IF not exists idx_leads_initial_audio_sent on public.leads using btree (initial_audio_sent) TABLESPACE pg_default;

create index IF not exists idx_leads_valid_payment on public.leads using btree (is_valid_nautico_payment) TABLESPACE pg_default
where
  (is_valid_nautico_payment = true);

create index IF not exists idx_leads_ai_paused on public.leads using btree (ai_paused) TABLESPACE pg_default
where
  (ai_paused = true);

create index IF not exists idx_leads_property_type on public.leads using btree (property_type) TABLESPACE pg_default
where
  (property_type is not null);

create index IF not exists idx_leads_interests on public.leads using gin (interests) TABLESPACE pg_default;

create index IF not exists idx_leads_objections on public.leads using gin (objections) TABLESPACE pg_default;

create index IF not exists idx_leads_phone_alt on public.leads using btree (phone) TABLESPACE pg_default
where
  (phone is not null);

create trigger update_leads_updated_at BEFORE
update on leads for EACH row
execute FUNCTION update_updated_at_column ();
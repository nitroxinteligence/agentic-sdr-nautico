-- =====================================================
-- POLÍTICAS RLS (ROW LEVEL SECURITY) PARA TODAS AS TABELAS
-- SDR IA Solar Prime - Configuração de Segurança
-- =====================================================

-- Habilitar RLS em todas as tabelas
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.follow_ups ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leads_qualifications ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- POLÍTICAS PARA TABELA: LEADS
-- =====================================================

-- Política para permitir SELECT para usuários autenticados
CREATE POLICY "leads_select_policy" ON public.leads
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Política para permitir INSERT para usuários autenticados
CREATE POLICY "leads_insert_policy" ON public.leads
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir UPDATE para usuários autenticados
CREATE POLICY "leads_update_policy" ON public.leads
    FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir DELETE para usuários autenticados
CREATE POLICY "leads_delete_policy" ON public.leads
    FOR DELETE
    USING (auth.role() = 'authenticated');

-- =====================================================
-- POLÍTICAS PARA TABELA: CONVERSATIONS
-- =====================================================

-- Política para permitir SELECT para usuários autenticados
CREATE POLICY "conversations_select_policy" ON public.conversations
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Política para permitir INSERT para usuários autenticados
CREATE POLICY "conversations_insert_policy" ON public.conversations
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir UPDATE para usuários autenticados
CREATE POLICY "conversations_update_policy" ON public.conversations
    FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir DELETE para usuários autenticados
CREATE POLICY "conversations_delete_policy" ON public.conversations
    FOR DELETE
    USING (auth.role() = 'authenticated');

-- =====================================================
-- POLÍTICAS PARA TABELA: MESSAGES
-- =====================================================

-- Política para permitir SELECT para usuários autenticados
CREATE POLICY "messages_select_policy" ON public.messages
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Política para permitir INSERT para usuários autenticados
CREATE POLICY "messages_insert_policy" ON public.messages
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir UPDATE para usuários autenticados
CREATE POLICY "messages_update_policy" ON public.messages
    FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir DELETE para usuários autenticados
CREATE POLICY "messages_delete_policy" ON public.messages
    FOR DELETE
    USING (auth.role() = 'authenticated');

-- =====================================================
-- POLÍTICAS PARA TABELA: FOLLOW_UPS
-- =====================================================

-- Política para permitir SELECT para usuários autenticados
CREATE POLICY "follow_ups_select_policy" ON public.follow_ups
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Política para permitir INSERT para usuários autenticados
CREATE POLICY "follow_ups_insert_policy" ON public.follow_ups
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir UPDATE para usuários autenticados
CREATE POLICY "follow_ups_update_policy" ON public.follow_ups
    FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir DELETE para usuários autenticados
CREATE POLICY "follow_ups_delete_policy" ON public.follow_ups
    FOR DELETE
    USING (auth.role() = 'authenticated');

-- =====================================================
-- POLÍTICAS PARA TABELA: KNOWLEDGE_BASE
-- =====================================================

-- Política para permitir SELECT para usuários autenticados
CREATE POLICY "knowledge_base_select_policy" ON public.knowledge_base
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Política para permitir INSERT para usuários autenticados
CREATE POLICY "knowledge_base_insert_policy" ON public.knowledge_base
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir UPDATE para usuários autenticados
CREATE POLICY "knowledge_base_update_policy" ON public.knowledge_base
    FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir DELETE para usuários autenticados
CREATE POLICY "knowledge_base_delete_policy" ON public.knowledge_base
    FOR DELETE
    USING (auth.role() = 'authenticated');

-- =====================================================
-- POLÍTICAS PARA TABELA: ANALYTICS
-- =====================================================

-- Política para permitir SELECT para usuários autenticados
CREATE POLICY "analytics_select_policy" ON public.analytics
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Política para permitir INSERT para usuários autenticados
CREATE POLICY "analytics_insert_policy" ON public.analytics
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir UPDATE para usuários autenticados
CREATE POLICY "analytics_update_policy" ON public.analytics
    FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir DELETE para usuários autenticados
CREATE POLICY "analytics_delete_policy" ON public.analytics
    FOR DELETE
    USING (auth.role() = 'authenticated');

-- =====================================================
-- POLÍTICAS PARA TABELA: LEADS_QUALIFICATIONS
-- =====================================================

-- Política para permitir SELECT para usuários autenticados
CREATE POLICY "leads_qualifications_select_policy" ON public.leads_qualifications
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Política para permitir INSERT para usuários autenticados
CREATE POLICY "leads_qualifications_insert_policy" ON public.leads_qualifications
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir UPDATE para usuários autenticados
CREATE POLICY "leads_qualifications_update_policy" ON public.leads_qualifications
    FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir DELETE para usuários autenticados
CREATE POLICY "leads_qualifications_delete_policy" ON public.leads_qualifications
    FOR DELETE
    USING (auth.role() = 'authenticated');

-- =====================================================
-- POLÍTICAS ADICIONAIS PARA SERVICE ROLE
-- =====================================================

-- Permitir acesso total para service_role (usado pela aplicação)
-- Esta política é necessária para que a aplicação funcione corretamente

-- Política para service_role em todas as tabelas
CREATE POLICY "service_role_all_access_leads" ON public.leads
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "service_role_all_access_conversations" ON public.conversations
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "service_role_all_access_messages" ON public.messages
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "service_role_all_access_follow_ups" ON public.follow_ups
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "service_role_all_access_knowledge_base" ON public.knowledge_base
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "service_role_all_access_analytics" ON public.analytics
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "service_role_all_access_leads_qualifications" ON public.leads_qualifications
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- =====================================================
-- VERIFICAÇÃO DAS POLÍTICAS CRIADAS
-- =====================================================

-- Query para verificar todas as políticas RLS criadas
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, policyname;

-- Query para verificar se RLS está habilitado nas tabelas
-- SELECT schemaname, tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- AND tablename IN ('leads', 'conversations', 'messages', 'follow_ups', 'knowledge_base', 'analytics', 'leads_qualifications')
-- ORDER BY tablename;
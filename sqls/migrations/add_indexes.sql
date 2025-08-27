-- Migration script to add indexes for improved query performance

-- Index on follow_ups.scheduled_at for faster retrieval of pending follow-ups
CREATE INDEX IF NOT EXISTS idx_follow_ups_scheduled_at 
ON follow_ups (scheduled_at);

-- Composite index on follow_ups.status and follow_ups.scheduled_at 
-- for efficient querying of pending follow-ups
CREATE INDEX IF NOT EXISTS idx_follow_ups_status_scheduled_at 
ON follow_ups (status, scheduled_at);

-- Index on follow_ups.lead_id for faster lookup of follow-ups by lead
CREATE INDEX IF NOT EXISTS idx_follow_ups_lead_id 
ON follow_ups (lead_id);

-- Index on leads.phone_number for faster lookup of leads by phone
CREATE INDEX IF NOT EXISTS idx_leads_phone_number 
ON leads (phone_number);

-- Index on leads_qualifications.lead_id for faster lookup of qualifications by lead
CREATE INDEX IF NOT EXISTS idx_leads_qualifications_lead_id 
ON leads_qualifications (lead_id);

-- Index on conversations.lead_id for faster lookup of conversations by lead
CREATE INDEX IF NOT EXISTS idx_conversations_lead_id 
ON conversations (lead_id);

-- Index on conversations.updated_at for faster lookup of recent conversations
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at 
ON conversations (updated_at);

COMMENT ON INDEX idx_follow_ups_scheduled_at IS 'Index for faster retrieval of follow-ups by scheduled time';
COMMENT ON INDEX idx_follow_ups_status_scheduled_at IS 'Composite index for efficient querying of pending follow-ups';
COMMENT ON INDEX idx_follow_ups_lead_id IS 'Index for faster lookup of follow-ups by lead ID';
COMMENT ON INDEX idx_leads_phone_number IS 'Index for faster lookup of leads by phone number';
COMMENT ON INDEX idx_leads_qualifications_lead_id IS 'Index for faster lookup of qualifications by lead ID';
COMMENT ON INDEX idx_conversations_lead_id IS 'Index for faster lookup of conversations by lead ID';
COMMENT ON INDEX idx_conversations_updated_at IS 'Index for faster lookup of recent conversations';
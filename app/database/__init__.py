"""
Database module initialization
"""

# SupabaseClient movido para app/integrations/supabase_client.py
from app.integrations.supabase_client import SupabaseClient

__all__ = ['SupabaseClient']

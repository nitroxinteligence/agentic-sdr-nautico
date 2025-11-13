import pytest
import asyncio
import os
from datetime import datetime, timezone, timedelta

os.environ.setdefault("SUPABASE_URL", "https://dummy.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "dummy-key")

from app.services.followup_executor_service import FollowUpSchedulerService


class DummyRedis:
    async def acquire_lock(self, key, ttl=60):
        return True

    async def enqueue(self, queue, payload):
        return True

    async def get(self, key):
        return None

    async def set(self, key, value, ttl=300):
        return True

    async def release_lock(self, key):
        return True


class DummyDB:
    def __init__(self, messages):
        self._messages = messages
        self.updated_status = {}

    async def get_pending_follow_ups(self):
        now = datetime.now(timezone.utc)
        return [{
            'id': 'fu-100',
            'lead_id': 'lead-1',
            'phone_number': '5581999999999',
            'scheduled_at': (now + timedelta(seconds=1)).isoformat(),
            'follow_up_type': 'reminder'
        }]

    async def update_follow_up_status(self, followup_id, status, *args, **kwargs):
        self.updated_status[followup_id] = status
        return {'id': followup_id, 'status': status}

    async def get_conversation_by_phone(self, phone):
        return {'id': 'conv-1'}

    async def get_conversation_messages(self, conversation_id, limit=50):
        return self._messages

    async def get_recent_followup_count(self, lead_id, since):
        return 0


@pytest.mark.asyncio
async def test_scheduler_cancels_when_user_replied():
    last_agent_time = datetime.now(timezone.utc) - timedelta(hours=1)
    last_user_time = datetime.now(timezone.utc) - timedelta(minutes=30)

    messages = [
        {'role': 'assistant', 'content': [{'type': 'text', 'text': 'msg'}], 'created_at': last_agent_time.isoformat()},
        {'role': 'user', 'content': [{'type': 'text', 'text': 'reply'}], 'created_at': last_user_time.isoformat()},
    ]

    svc = FollowUpSchedulerService()
    svc.redis = DummyRedis()
    svc.db = DummyDB(messages)

    await svc.enqueue_pending_followups()

    assert svc.db.updated_status.get('fu-100') == 'cancelled'

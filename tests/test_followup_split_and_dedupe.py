import asyncio
import types
import os
import pytest

# Garantir variáveis de ambiente mínimas para import dos serviços
os.environ.setdefault("SUPABASE_URL", "https://dummy.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "dummy-key")

from app.integrations.evolution import EvolutionAPIClient
from app.services.followup_service_100_real import FollowUpServiceReal


class DummyResponse:
    def __init__(self):
        self.status_code = 200
        self._json = {"key": {"id": "msg-id-1"}}

    def json(self):
        return self._json


@pytest.mark.asyncio
async def test_send_text_message_no_split(monkeypatch):
    client = EvolutionAPIClient()

    calls = {"count": 0}

    async def fake_request(method, path, **kwargs):
        calls["count"] += 1
        return DummyResponse()

    monkeypatch.setattr(client, "_make_request", fake_request)

    long_message = (
        "Oi! Esta é uma mensagem longa com várias frases. "
        "Ela normalmente seria dividida em partes, mas aqui não deve. "
        "Enviaremos como uma única mensagem."
    )

    result = await client.send_text_message(
        phone="5581999999999", message=long_message, simulate_typing=False, split=False
    )

    assert result.get("key", {}).get("id") == "msg-id-1"
    assert calls["count"] == 1


@pytest.mark.asyncio
async def test_send_text_message_word_split_20(monkeypatch):
    client = EvolutionAPIClient()

    calls = {"count": 0}

    async def fake_request(method, path, **kwargs):
        calls["count"] += 1
        return DummyResponse()

    monkeypatch.setattr(client, "_make_request", fake_request)

    words = [str(i) for i in range(0, 55)]
    long_message = " ".join(words)

    result = await client.send_text_message(
        phone="5581999999999",
        message=long_message,
        simulate_typing=False,
        split=True,
        force_word_split=True,
        max_words_override=20,
    )

    assert result.get("key", {}).get("id") == "msg-id-1"
    # 55 palavras -> 3 partes (20,20,15)
    assert calls["count"] == 3


class DummySupabaseTable:
    def __init__(self, data):
        self._data = data

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def gte(self, *args, **kwargs):
        return self

    def lte(self, *args, **kwargs):
        return self

    def execute(self):
        return types.SimpleNamespace(data=self._data)


class DummySupabaseClient:
    def __init__(self):
        self._tables = {}

    def table(self, name):
        return self._tables.get(name, DummySupabaseTable([]))


@pytest.mark.asyncio
async def test_schedule_followup_dedupe(monkeypatch):
    service = FollowUpServiceReal()
    await service.initialize()

    dummy_client = DummySupabaseClient()
    # Simular já existir um follow-up pendente na janela
    dummy_client._tables["follow_ups"] = DummySupabaseTable([
        {"id": "fu-1", "scheduled_at": "2025-11-13T12:00:00+00:00", "status": "pending"}
    ])
    # Simular lead existente
    dummy_client._tables["leads"] = DummySupabaseTable([
        {"id": "lead-123", "phone_number": "5581999999999", "name": "Teste"}
    ])

    class DummyDB:
        def __init__(self, client):
            self.client = client

        async def create_follow_up(self, data):
            return {"id": "fu-new"}

    service.db = DummyDB(dummy_client)

    # Forçar lead_id válido via _get_or_create_supabase_lead_id
    async def fake_get_or_create(lead_info):
        return "lead-123"

    monkeypatch.setattr(service, "_get_or_create_supabase_lead_id", fake_get_or_create)

    lead_info = {"id": "lead-uuid", "phone_number": "5581999999999"}
    result = await service.schedule_followup(
        phone_number="5581999999999",
        message="Follow-up teste",
        delay_hours=0.0,
        lead_info=lead_info,
    )

    assert result.get("success") is False
    assert result.get("reason") == "duplicate_pending"

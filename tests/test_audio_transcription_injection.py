import os
import pytest
import asyncio

# Variáveis mínimas para inicializar serviços
os.environ.setdefault("SUPABASE_URL", "https://dummy.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "dummy-key")

from app.agents.agentic_sdr_stateless import AgenticSDRStateless


@pytest.mark.asyncio
async def test_audio_transcription_injected(monkeypatch):
    agent = AgenticSDRStateless()
    await agent.initialize()

    # Simular processamento multimodal retornando transcrição
    async def fake_process_media(media_data):
        return {
            "success": True,
            "type": "audio",
            "text": "Quero saber mais sobre o plano Vermelho de Luta",
            "metadata": {"duration": 10, "engine": "google"}
        }

    monkeypatch.setattr(agent.multimodal, "process_media", fake_process_media)

    message = "[voice]"
    execution_context = {
        "conversation_history": [],
        "lead_info": {"id": "lead-1", "name": "Mateus", "phone_number": "5581999999999"},
        "phone": "5581999999999",
        "media": {"type": "audio", "content": "data:audio/ogg;base64,AAAA"}
    }

    # Executa apenas a atualização de contexto para verificar injeção
    history, lead = await agent._update_context(message, [], execution_context["lead_info"], execution_context["media"])

    assert len(history) == 1
    parts = history[0]["content"]
    # Deve conter texto da transcrição como parte adicional
    assert any(p.get("type") == "text" and "[Áudio]" in p.get("text", "") for p in parts)

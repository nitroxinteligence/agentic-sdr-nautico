"""
Webhook para receber eventos do Kommo CRM
"""
from fastapi import APIRouter, Request, BackgroundTasks
from loguru import logger
from datetime import datetime
from typing import Dict, Any

from app.integrations.redis_client import redis_client
from app.config import settings

router = APIRouter(prefix="/webhook/kommo", tags=["kommo"])

async def process_lead_status_change(payload: Dict[str, Any]):
    """
    Processa a mudança de status de um lead vinda do Kommo.
    Ativa ou desativa a pausa do agente no Redis.
    """
    try:
        # A estrutura do payload pode variar, então usamos .get() de forma segura
        lead_data = payload.get('lead', {})
        if not lead_data:
            # Kommo às vezes envia o evento em uma lista dentro de uma chave com o nome do evento
            event_key = next((key for key in payload if isinstance(payload.get(key), list)), None)
            if event_key and payload[event_key]:
                lead_data = payload[event_key][0]
            else:
                logger.warning(f"Webhook Kommo: Estrutura de payload de lead não reconhecida: {payload}")
                return

        new_status_id = lead_data.get('status_id')
        custom_fields = lead_data.get('custom_fields', [])
        phone = None

        # Encontra o número de telefone nos campos customizados
        for field in custom_fields:
            # O campo de telefone pode ter nomes diferentes, verificamos alguns comuns
            if field.get('name', '').lower() in ['telefone', 'whatsapp', 'phone']:
                values = field.get('values', [])
                if values:
                    phone = values[0].get('value')
                    break
        
        if not phone:
            logger.warning(f"Webhook Kommo: Não foi possível encontrar o telefone para o lead ID {lead_data.get('id')}")
            return

        human_handoff_stage_id = settings.kommo_human_handoff_stage_id

        if str(new_status_id) == str(human_handoff_stage_id):
            # Ativa a pausa
            await redis_client.set_human_handoff_pause(phone)
            logger.info(f"PAUSA ATIVADA via Webhook Kommo para o lead com telefone {phone}")
        else:
            # Desativa a pausa se o lead for movido para qualquer outro estágio
            was_active = await redis_client.is_human_handoff_active(phone)
            if was_active:
                await redis_client.clear_human_handoff_pause(phone)
                logger.info(f"PAUSA DESATIVADA via Webhook Kommo para o lead com telefone {phone}")

    except Exception as e:
        logger.error(f"Erro ao processar webhook de mudança de status do Kommo: {e}", payload=payload)


@router.post("/events")
async def kommo_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Recebe eventos do Kommo CRM e os processa em background.
    """
    try:
        content_type = request.headers.get("content-type", "")
        data = None

        if "application/json" in content_type:
            try:
                data = await request.json()
            except Exception:
                # Corpo pode estar vazio mesmo com header JSON
                body = await request.body()
                if not body:
                    data = {"event": "ping_json_empty_body"}
                else:
                    logger.warning("Webhook Kommo: Falha ao decodificar JSON, corpo não vazio.")
                    data = {"raw_data": body.decode('utf-8', errors='ignore')}
        elif "application/x-www-form-urlencoded" in content_type:
            form_data = await request.form()
            data = dict(form_data)
        else:
            body = await request.body()
            if not body:
                data = {"event": "ping_empty_body"}
            else:
                data = {"raw_data": body.decode('utf-8', errors='ignore')}

        logger.debug(f"📥 Evento Kommo recebido: {data}")

        # O Kommo pode enviar eventos aninhados. Ex: {'update': [{'lead': ...}]}
        event_key = next((key for key in data if isinstance(data.get(key), list)), None)
        
        if event_key:
            for event_payload in data[event_key]:
                # Verificamos se a mudança de status está no payload
                if 'status_id' in event_payload:
                    background_tasks.add_task(process_lead_status_change, {'lead': event_payload})
        
        return {"status": "ok", "received_at": datetime.now().isoformat()}

    except Exception as e:
        logger.error(f"❌ Erro inesperado no webhook Kommo: {e}")
        return {"status": "ok", "error_handled": True}

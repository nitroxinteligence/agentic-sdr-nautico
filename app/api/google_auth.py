"""
Google OAuth 2.0 API Endpoints
Gerencia fluxo de autorização OAuth para Google Calendar
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import Optional
import logging

from app.integrations.google_oauth_handler import get_oauth_handler
from app.utils.logger import emoji_logger

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/google",
    tags=["Google OAuth"]
)


@router.get("/auth")
async def google_auth():
    """
    Inicia fluxo de autorização OAuth 2.0
    Redireciona o usuário para a tela de consentimento do Google
    """
    try:
        emoji_logger.service_call("GET /google/auth - Iniciando fluxo OAuth")

        logger.info("🔍 Verificando configuração OAuth...")
        logger.info(
            f"   Client ID configurado: "
            f"{'Sim' if get_oauth_handler().client_id else 'Não'}"
        )
        logger.info(
            f"   Client Secret configurado: "
            f"{'Sim' if get_oauth_handler().client_secret else 'Não'}"
        )
        logger.info(f"   Redirect URI: {get_oauth_handler().redirect_uri}")

        oauth_handler = get_oauth_handler()

        if not oauth_handler.client_id or not oauth_handler.client_secret:
            error_msg = (
                "OAuth não configurado. Verifique GOOGLE_OAUTH_CLIENT_ID e "
                "GOOGLE_OAUTH_CLIENT_SECRET no .env"
            )
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

        auth_url = oauth_handler.get_google_auth_url()

        if not auth_url:
            raise HTTPException(
                status_code=500,
                detail="Erro ao gerar URL de autorização."
            )

        emoji_logger.system_success(
            f"Redirecionando para Google OAuth: {auth_url[:50]}..."
        )

        return RedirectResponse(url=auth_url)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(
            f"❌ Erro detalhado no endpoint /google/auth:\n{error_trace}"
        )
        emoji_logger.service_error(f"Erro no endpoint /google/auth: {e}")

        return {
            "error": "Internal Server Error",
            "message": str(e),
            "details": "Verifique os logs para mais informações",
            "configuration": {
                "client_id_configured": bool(get_oauth_handler().client_id),
                "client_secret_configured": bool(
                    get_oauth_handler().client_secret
                ),
                "redirect_uri": get_oauth_handler().redirect_uri
            }
        }


@router.get("/callback")
async def google_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    state: Optional[str] = Query(None)
):
    """
    Callback do Google OAuth 2.0
    Recebe o código de autorização e troca por tokens
    """
    try:
        emoji_logger.service_call(
            f"GET /google/callback - Code: {code[:20] if code else 'None'}..."
        )

        if error:
            emoji_logger.service_error(f"Erro no callback OAuth: {error}")
            return HTMLResponse(
                content=f"""
                <html>
                <head><title>Erro na Autorização</title></head>
                <body><h1>❌ Erro na Autorização</h1><p>{error}</p></body>
                </html>
                """,
                status_code=400
            )

        if not code:
            raise HTTPException(
                status_code=400,
                detail="Código de autorização não fornecido"
            )

        oauth_handler = get_oauth_handler()
        result = await oauth_handler.handle_google_callback(code)

        if result.get("success"):
            emoji_logger.system_success(
                "✅ Autorização OAuth concluída com sucesso!"
            )
            test_result = await oauth_handler.test_connection()
            return HTMLResponse(
                content=f"""
                <html>
                <head><title>Autorização Concluída</title></head>
                <body>
                    <h1>✅ Autorização Concluída!</h1>
                    <p>Email: {test_result.get('user_email', 'N/A')}</p>
                    <p>Calendário: {test_result.get('calendar_id', 'N/A')}</p>
                </body>
                </html>
                """
            )
        else:
            emoji_logger.service_error(
                f"Erro ao processar callback: {result.get('message')}"
            )
            return HTMLResponse(
                content=f"""
                <html>
                <head><title>Erro na Autorização</title></head>
                <body>
                    <h1>❌ Erro ao Processar Autorização</h1>
                    <p>{result.get('message', 'Erro desconhecido')}</p>
                </body>
                </html>
                """,
                status_code=500
            )

    except Exception as e:
        emoji_logger.service_error(f"Erro no callback OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def google_oauth_status():
    """
    Verifica status da conexão OAuth com Google Calendar
    """
    try:
        oauth_handler = get_oauth_handler()
        result = await oauth_handler.test_connection()

        if result.get("success"):
            emoji_logger.system_success(
                f"OAuth conectado: {result.get('user_email')}"
            )
        else:
            emoji_logger.service_warning("OAuth não configurado ou expirado")

        return {
            "oauth_configured": result.get("success", False),
            "user_email": result.get("user_email"),
            "calendar_id": result.get("calendar_id"),
            "can_create_meets": result.get("can_create_meets", False),
            "can_invite_attendees": result.get(
                "can_invite_attendees",
                False
            ),
            "message": result.get("message"),
            "auth_url": "/google/auth" if not result.get("success") else None
        }

    except Exception as e:
        emoji_logger.service_error(f"Erro ao verificar status OAuth: {e}")
        return {
            "oauth_configured": False,
            "message": str(e),
            "auth_url": "/google/auth"
        }

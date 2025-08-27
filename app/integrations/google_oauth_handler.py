"""
Google OAuth 2.0 Handler - Arquitetura Modular Simples
Gerencia autenticação OAuth para Google Calendar com suporte a Google Meet e Participantes
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings
from app.utils.logger import emoji_logger


class GoogleOAuthHandler:
    """
    Handler OAuth 2.0 para Google Calendar
    Zero complexidade, máxima funcionalidade
    """

    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events',
    ]

    def __init__(self):
        """Inicializa o handler OAuth"""
        self.client_id = settings.google_oauth_client_id
        self.client_secret = settings.google_oauth_client_secret
        self.redirect_uri = settings.google_oauth_redirect_uri
        self.refresh_token = settings.google_oauth_refresh_token
        self._credentials: Optional[Credentials] = None
        self._credentials_expire: Optional[datetime] = None
        emoji_logger.service_info("🔐 GoogleOAuthHandler inicializado")

    def get_google_auth_url(self) -> str:
        """
        Gera URL de autorização OAuth para o usuário
        """
        try:
            emoji_logger.service_info(
                f"🔐 Gerando URL OAuth com Client ID: {self.client_id[:20]}..."
            )
            if not self.client_id or not self.client_secret:
                emoji_logger.service_error(
                    "❌ Client ID ou Secret não configurados!"
                )
                raise ValueError(
                    "Google OAuth Client ID e Secret devem estar configurados"
                )
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                    }
                },
                scopes=self.SCOPES
            )
            flow.redirect_uri = self.redirect_uri
            emoji_logger.service_info(
                f"🔗 Redirect URI configurado: {self.redirect_uri}"
            )
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            emoji_logger.service_info(
                f"✅ URL de autorização gerada: {authorization_url[:50]}..."
            )
            authorization_url = authorization_url.replace('+', '%20')
            emoji_logger.service_info(
                f"🔧 URL corrigida: {authorization_url[:50]}..."
            )
            return authorization_url
        except Exception as e:
            emoji_logger.service_error(
                f"❌ Erro ao gerar URL de autorização: {e}"
            )
            raise

    async def handle_google_callback(self, code: str) -> Dict[str, Any]:
        """
        Processa callback do Google após autorização
        """
        try:
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                    }
                },
                scopes=self.SCOPES
            )
            flow.redirect_uri = self.redirect_uri
            flow.fetch_token(code=code)
            credentials = flow.credentials
            if credentials.refresh_token:
                emoji_logger.service_info(
                    "✅ Novo refresh token gerado. Salve na variável de "
                    "ambiente GOOGLE_OAUTH_REFRESH_TOKEN."
                )
                emoji_logger.service_info(f"TOKEN: {credentials.refresh_token}")
                return {
                    "success": True,
                    "message": "Autorização concluída. Copie o refresh token.",
                    "access_token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "expiry": (
                        credentials.expiry.isoformat()
                        if credentials.expiry else None
                    ),
                    "scopes": credentials.scopes
                }
            else:
                emoji_logger.service_warning("⚠️ Refresh token não obtido")
                return {
                    "success": False,
                    "message": "Refresh token não obtido. Tente novamente.",
                    "access_token": credentials.token
                }
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro no callback OAuth: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar autorização: {str(e)}"
            }

    def get_credentials(self) -> Optional[Credentials]:
        """
        Obtém credenciais OAuth válidas
        """
        try:
            if self._credentials and self._credentials.valid:
                return self._credentials
            if not self.refresh_token:
                emoji_logger.service_warning("⚠️ Refresh token não disponível")
                return None
            credentials = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.SCOPES
            )
            if not credentials.valid:
                request = Request()
                credentials.refresh(request)
                emoji_logger.service_info("🔄 Access token renovado com sucesso")
            self._credentials = credentials
            return credentials
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao obter credenciais: {e}")
            return None

    def build_calendar_service(self):
        """
        Constrói serviço do Google Calendar com credenciais OAuth
        """
        try:
            credentials = self.get_credentials()
            if not credentials:
                emoji_logger.service_error("❌ Credenciais não disponíveis")
                return None
            service = build('calendar', 'v3', credentials=credentials)
            emoji_logger.service_info(
                "✅ Serviço Google Calendar construído com OAuth"
            )
            return service
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao construir serviço: {e}")
            return None

    async def test_connection(self) -> Dict[str, Any]:
        """
        Testa conexão com Google Calendar API
        """
        try:
            service = self.build_calendar_service()
            if not service:
                return {
                    "success": False,
                    "message": "Serviço não disponível - autorização necessária"
                }
            calendar_list = service.calendarList().list().execute()
            primary_calendar = next(
                (
                    cal for cal in calendar_list.get('items', [])
                    if cal.get('primary')
                ),
                None
            )
            if primary_calendar:
                user_email = primary_calendar.get('summary', 'Unknown')
                calendar_id = primary_calendar.get('id')
                emoji_logger.service_info(f"✅ Conectado como: {user_email}")
                return {
                    "success": True,
                    "message": "Conexão estabelecida com sucesso",
                    "user_email": user_email,
                    "calendar_id": calendar_id,
                    "calendars": len(calendar_list.get('items', [])),
                    "can_create_meets": True,
                    "can_invite_attendees": True
                }
            else:
                return {
                    "success": False, "message": "Nenhum calendário encontrado"
                }
        except HttpError as e:
            emoji_logger.service_error(f"❌ Erro HTTP ao testar conexão: {e}")
            return {
                "success": False,
                "message": f"Erro de API: {e.reason}",
                "status_code": e.resp.status
            }
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao testar conexão: {e}")
            return {"success": False, "message": f"Erro: {str(e)}"}

    def create_event_with_meet(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[str] = None,
        description: str = None,
        location: str = None
    ) -> Dict[str, Any]:
        """
        Cria evento com Google Meet e participantes
        """
        try:
            service = self.build_calendar_service()
            if not service:
                return {
                    "success": False,
                    "message": "Serviço não disponível - autorização necessária"
                }
            event = {
                'summary': title,
                'description': description or '',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': settings.timezone or 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': settings.timezone or 'America/Sao_Paulo',
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f'meet-{datetime.now().timestamp()}',
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                },
                'attendees': [{'email': email} for email in (attendees or [])],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            if location:
                event['location'] = location
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            meet_link = None
            if 'conferenceData' in created_event:
                entry_points = created_event['conferenceData'].get(
                    'entryPoints', []
                )
                for entry in entry_points:
                    if entry.get('entryPointType') == 'video':
                        meet_link = entry.get('uri')
                        break
            emoji_logger.service_info(
                f"✅ Evento criado com Google Meet!\n" 
                f"   📅 ID: {event_id}\n" 
                f"   🔗 Calendar: {event_link}\n" 
                f"   📹 Meet: {meet_link}\n" 
                f"   👥 Participantes: {len(attendees or [])}"
            )
            return {
                "success": True, "event_id": event_id,
                "event_link": event_link, "meet_link": meet_link,
                "title": title, "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(), "attendees": attendees or [],
                "message": "Evento criado com sucesso com Google Meet!"
            }
        except HttpError as e:
            emoji_logger.service_error(f"❌ Erro HTTP ao criar evento: {e}")
            return {
                "success": False,
                "message": f"Erro de API: {e.reason}",
                "status_code": e.resp.status
            }
        except Exception as e:
            emoji_logger.service_error(f"❌ Erro ao criar evento: {e}")
            return {"success": False, "message": f"Erro: {str(e)}"}


_oauth_handler: Optional[GoogleOAuthHandler] = None


def get_oauth_handler() -> GoogleOAuthHandler:
    """
    Obtém instância singleton do OAuth handler
    """
    global _oauth_handler
    if _oauth_handler is None:
        _oauth_handler = GoogleOAuthHandler()
    return _oauth_handler
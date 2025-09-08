"""
CRM Service 100% REAL - Kommo API
ZERO simulação, MÁXIMA simplicidade
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import aiohttp
import json
import random
from functools import wraps
from app.utils.logger import emoji_logger
from app.config import settings
from app.services.rate_limiter import wait_for_kommo
from app.decorators.error_handler import handle_kommo_errors
from app.exceptions import KommoAPIException
from app.integrations.redis_client import redis_client


def async_retry_with_backoff(
    max_retries: int = 3, initial_delay: float = 1.0,
    max_delay: float = 30.0, backoff_factor: float = 2.0
):
    """Decorator para retry assíncrono com backoff exponencial"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        jitter = random.uniform(0, delay * 0.1)
                        sleep_time = min(delay + jitter, max_delay)
                        emoji_logger.service_warning(
                            f"Tentativa {attempt + 1}/{max_retries} falhou: {e}. "
                            f"Aguardando {sleep_time:.1f}s..."
                        )
                        await asyncio.sleep(sleep_time)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        emoji_logger.service_error(
                            f"Todas as {max_retries} tentativas falharam: {e}"
                        )
                except Exception as e:
                    raise e
            if last_exception:
                raise last_exception
        return wrapper
    return decorator


class CRMServiceReal:
    """Serviço REAL de CRM - Kommo API"""

    def __init__(self):
        self.is_initialized = False
        self.base_url = (
            settings.kommo_base_url or "https://nautico.kommo.com"
        )
        self.access_token = settings.kommo_long_lived_token
        self.pipeline_id = int(settings.kommo_pipeline_id or 11672895)
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        self._session_timeout = aiohttp.ClientTimeout(total=30)
        self._stages_cache = None
        self._cache_ttl = 3600
        self._cache_timestamp = None
        self.custom_fields = {
            "phone": None, "whatsapp": None, "bill_value": None,
            "valor_conta": None, "solution_type": None,
            "plano_socio": None, "calendar_link": None,
            "google_calendar": None, "conversation_id": None
        }
        self.stage_map = {}
        self.membership_plan_values = {
            "sócio contribuinte": 326358, "socio contribuinte": 326358,
            "sócio patrimonial": 326360, "socio patrimonial": 326360,
            "sócio remido": 326362, "socio remido": 326362,
            "sócio benemérito": 326364, "socio benemerito": 326364,
            "não definido": 326366, "nao definido": 326366,
            "programa fidelidade": 1078618, "cartão torcedor": 1078620,
            "plano especial": 1078622
        }
        self.membership_plan_options = {
            "Sócio Contribuinte": 326358, "Sócio Patrimonial": 326360,
            "Sócio Remido": 326362, "Sócio Benemérito": 326364,
            "Não Definido": 326366, "Programa Fidelidade": 1078618,
            "Cartão Torcedor": 1078620, "Plano Especial": 1078622
        }

    async def _get_session(self):
        connector = aiohttp.TCPConnector(
            limit=10, limit_per_host=5, ttl_dns_cache=300
        )
        return aiohttp.ClientSession(
            connector=connector, timeout=self._session_timeout
        )

    @handle_kommo_errors(max_retries=3, delay=10.0)
    async def initialize(self):
        """Inicializa conexão REAL com Kommo CRM"""
        if self.is_initialized:
            return
            
        # Verificar se CRM está habilitado
        if not settings.enable_kommo_crm:
            emoji_logger.system_warning("Kommo CRM desabilitado - pulando inicialização")
            return
            
        try:
            await wait_for_kommo()
            async with await self._get_session() as session:
                async with session.get(
                    f"{self.base_url}/api/v4/account", headers=self.headers
                ) as response:
                    if response.status == 200:
                        account = await response.json()
                        emoji_logger.service_ready(
                            f"✅ Kommo CRM conectado: {account.get('name', 'CRM')}"
                        )
                        await self._fetch_custom_fields()
                        await self._fetch_pipeline_stages()
                        self.is_initialized = True
                    else:
                        error_text = await response.text()
                        raise KommoAPIException(
                            f"Erro ao conectar Kommo: {response.status} - {error_text}",
                            error_code="KOMMO_CONNECTION_ERROR",
                            details={
                                "status_code": response.status,
                                "response": error_text
                            }
                        )
        except Exception as e:
            emoji_logger.service_error(f"Erro ao conectar Kommo: {e}")
            if not isinstance(e, KommoAPIException):
                raise KommoAPIException(
                    f"Erro ao conectar Kommo: {e}",
                    error_code="KOMMO_INITIALIZATION_ERROR",
                    details={"exception": str(e)}
                )
            else:
                raise

    async def _fetch_custom_fields(self):
        """Busca IDs dos campos customizados dinamicamente"""
        try:
            await wait_for_kommo()
            
            async with await self._get_session() as session:
                url = f"{self.base_url}/api/v4/leads/custom_fields"
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        fields = await response.json()
                        
                        field_mapping = {
                            "telefone": "phone",
                            "whatsapp": "whatsapp", 
                            "valor conta": "bill_value",
                            "tipo solução": "solution_type",
                            "link do evento no google calendar": "calendar_link",
                            "interesse socio": "membership_interest",
                            "plano sócio": "membership_plan",
                            "local da instalação": "location",
                            "score qualificação": "score",
                            "id conversa": "conversation_id"
                        }
                        
                        for field in fields.get("_embedded", {}).get("custom_fields", []):
                            field_name = field.get("name", "").strip().lower()
                            field_id = field.get("id")
                            
                            for key, mapped_name in field_mapping.items():
                                if key in field_name:
                                    self.custom_fields[mapped_name] = field_id
                                    break
                        
                        emoji_logger.service_info(f"📊 {len([v for v in self.custom_fields.values() if v])} campos customizados mapeados")
                        
        except Exception as e:
            emoji_logger.service_warning(f"Erro ao buscar campos customizados: {str(e)}")
            # Continuar mesmo com erro - não bloquear startup

    async def _fetch_pipeline_stages(self):
        """Busca estágios do pipeline dinamicamente, criando um mapa resiliente."""
        import time
        import unicodedata

        if (self._stages_cache and
                (time.time() - self._cache_timestamp) < self._cache_ttl):
            self.stage_map = self._stages_cache
            return

        def normalize_text(text: str) -> str:
            """Remove acentos e caracteres especiais."""
            return "".join(
                c for c in unicodedata.normalize('NFD', text)
                if unicodedata.category(c) != 'Mn'
            )

        try:
            await wait_for_kommo()
            async with await self._get_session() as session:
                async with session.get(
                    f"{self.base_url}/api/v4/leads/pipelines",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        pipelines = await response.json()
                        for pipeline in pipelines.get("_embedded", {}).get("pipelines", []):
                            if pipeline.get("id") == self.pipeline_id:
                                self.stage_map = {}
                                for status in pipeline.get("_embedded", {}).get("statuses", []):
                                    stage_name = status.get("name", "")
                                    stage_id = status.get("id")
                                    if not stage_name or not stage_id:
                                        continue

                                    # Adiciona múltiplas variações ao mapa para robustez
                                    variations = {
                                        stage_name.lower(),
                                        stage_name.upper(),
                                        stage_name.lower().replace(" ", "_"),
                                        normalize_text(stage_name.lower()),
                                        normalize_text(stage_name.lower().replace(" ", "_"))
                                    }
                                    for var in variations:
                                        self.stage_map[var] = stage_id
                                
                                self._stages_cache = self.stage_map
                                self._cache_timestamp = time.time()
                                emoji_logger.service_info(
                                    f"📊 {len(self.stage_map)} variações de estágios mapeadas"
                                )
                                break
        except Exception as e:
            emoji_logger.service_warning(f"Erro ao buscar estágios: {e}")
            # A verificação de estágios essenciais pode ser adicionada aqui se necessário

    @async_retry_with_backoff()
    @handle_kommo_errors()
    async def create_lead(
            self, lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria lead REAL no Kommo"""
        if not self.is_initialized:
            await self.initialize()
        try:
            # Garantir que name nunca seja None/null para o Kommo
            lead_name = lead_data.get("name")
            if not lead_name:  # None, empty string, ou falsy
                lead_name = "Lead sem nome"
            
            # Inicializar tags com SDR_IA
            tags = [{"name": "SDR_IA"}]
            
            # Adicionar tag baseada no chosen_flow se disponível
            if lead_data.get("chosen_flow"):
                chosen_flow = lead_data["chosen_flow"]
                # Mapear chosen_flow para tag correspondente
                flow_to_tag_map = {
                    "Instalação Usina Própria": "Instalação Usina Própria",
                    "Aluguel de Lote": "Aluguel de Lote",
                    "Compra com Desconto": "Compra com Desconto",
                    "Usina Investimento": "Usina Investimento"
                }
                tag_name = flow_to_tag_map.get(chosen_flow)
                if tag_name:
                    tags.append({"name": tag_name})
            
            kommo_lead = {
                "name": lead_name,
                "pipeline_id": self.pipeline_id,
                "_embedded": {"tags": tags}
            }
            
            custom_fields = []
            # Adicionar telefone como campo customizado (phone e whatsapp)
            if lead_data.get("phone"):
                # Adicionar ao campo phone se existir
                if self.custom_fields.get("phone"):
                    custom_fields.append({
                        "field_id": self.custom_fields["phone"],
                        "values": [{
                            "value": lead_data["phone"]
                        }]
                    })
                # Adicionar ao campo whatsapp se existir
                if self.custom_fields.get("whatsapp"):
                    custom_fields.append({
                        "field_id": self.custom_fields["whatsapp"],
                        "values": [{
                            "value": lead_data["phone"]
                        }]
                    })
            if lead_data.get("bill_value"):
                custom_fields.append({
                    "field_id": self.custom_fields.get("bill_value", 392804),
                    "values": [{"value": lead_data["bill_value"]}]
                })
            if lead_data.get("chosen_membership_plan"):
                enum_id = self.membership_plan_values.get(
                    lead_data["chosen_membership_plan"].lower()
                )
                if enum_id:
                    custom_fields.append({
                        "field_id": self.custom_fields.get(
                            "membership_plan", 392808
                        ),
                        "values": [{"enum_id": enum_id}]
                    })
            if lead_data.get("google_event_link"):
                custom_fields.append({
                    "field_id": self.custom_fields.get(
                        "calendar_link", 395520
                    ),
                    "values": [{"value": lead_data["google_event_link"]}]
                })
            if custom_fields:
                kommo_lead["custom_fields_values"] = custom_fields
            await wait_for_kommo()
            async with await self._get_session() as session:
                async with session.post(
                    f"{self.base_url}/api/v4/leads",
                    headers=self.headers,
                    json=[kommo_lead]
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        lead_id = result.get(
                            "_embedded", {}
                        ).get("leads", [{}])[0].get("id")
                        emoji_logger.team_crm(
                            f"✅ Lead CRIADO no Kommo: {kommo_lead['name']} - "
                            f"ID: {lead_id}"
                        )
                        return {
                            "success": True, "lead_id": lead_id,
                            "message": "Lead criado com sucesso"
                        }
                    else:
                        error_text = await response.text()
                        raise KommoAPIException(
                            f"Erro ao criar lead: {response.status} - {error_text}",
                            error_code="KOMMO_CREATE_LEAD_ERROR",
                            details={
                                "status_code": response.status,
                                "response": error_text
                            }
                        )
        except Exception as e:
            emoji_logger.service_error(f"Erro ao criar lead no Kommo: {e}")
            if not isinstance(e, KommoAPIException):
                raise KommoAPIException(
                    f"Erro ao criar lead: {e}",
                    error_code="KOMMO_CREATE_LEAD_EXCEPTION",
                    details={"exception": str(e)}
                )
            else:
                raise

    @async_retry_with_backoff()
    @handle_kommo_errors()
    async def update_lead(
            self, lead_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atualiza lead REAL no Kommo, incluindo campos customizados e tags."""
        if not self.is_initialized:
            await self.initialize()
        try:
            kommo_update = {}
            if update_data.get("name"):
                kommo_update["name"] = update_data["name"]
            
            # Handle stage update
            if update_data.get("current_stage"):
                normalized_stage = update_data["current_stage"].strip().lower().replace(" ", "_")
                stage_id = self.stage_map.get(normalized_stage)
                if stage_id:
                    kommo_update["status_id"] = stage_id
                else:
                    emoji_logger.service_warning(f"Estágio '{update_data['current_stage']}' não encontrado no mapa.")

            # Handle custom fields
            custom_fields = []
            
            # Handle phone fields separately (phone and whatsapp)
            if update_data.get("phone"):
                # Adicionar ao campo phone se existir
                if self.custom_fields.get("phone"):
                    custom_fields.append({
                        "field_id": self.custom_fields["phone"],
                        "values": [{"value": update_data["phone"]}]
                    })
                # Adicionar ao campo whatsapp se existir
                if self.custom_fields.get("whatsapp"):
                    custom_fields.append({
                        "field_id": self.custom_fields["whatsapp"],
                        "values": [{"value": update_data["phone"]}]
                    })
            
            field_map = {
                "bill_value": self.custom_fields.get("bill_value"),
                "chosen_membership_plan": self.custom_fields.get("membership_plan"),
                "google_event_link": self.custom_fields.get("calendar_link")
            }

            for key, field_id in field_map.items():
                if key in update_data and field_id:
                    value = update_data[key]
                    if key == "chosen_membership_plan":
                        enum_id = self.membership_plan_values.get(str(value).lower())
                        if enum_id:
                            custom_fields.append({"field_id": field_id, "values": [{"enum_id": enum_id}]})
                    else:
                        custom_fields.append({"field_id": field_id, "values": [{"value": value}]})
            
            if custom_fields:
                kommo_update["custom_fields_values"] = custom_fields

            # Handle tags
            tags_to_add = update_data.get("tags")
            if tags_to_add:
                 kommo_update["_embedded"] = {"tags": [{"name": tag} for tag in tags_to_add]}


            if not kommo_update:
                return {"success": True, "message": "Nenhum dado para atualizar"}

            await wait_for_kommo()
            async with await self._get_session() as session:
                async with session.patch(
                    f"{self.base_url}/api/v4/leads/{lead_id}",
                    headers=self.headers,
                    json=kommo_update
                ) as response:
                    if response.status == 200:
                        emoji_logger.team_crm(f"✅ Lead {lead_id} ATUALIZADO no Kommo")
                        return {"success": True, "message": "Lead atualizado com sucesso"}
                    else:
                        error_text = await response.text()
                        raise KommoAPIException(
                            f"Erro ao atualizar lead: {response.status} - {error_text}",
                            error_code="KOMMO_UPDATE_LEAD_ERROR",
                            details={"status_code": response.status, "response": error_text, "payload": kommo_update}
                        )
        except Exception as e:
            emoji_logger.service_error(f"Erro ao atualizar lead no Kommo: {e}")
            if not isinstance(e, KommoAPIException):
                raise KommoAPIException(
                    f"Erro ao atualizar lead: {e}",
                    error_code="KOMMO_UPDATE_LEAD_EXCEPTION",
                    details={"exception": str(e)}
                )
            else:
                raise

    async def create_or_update_lead(
            self, lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria ou atualiza lead REAL no Kommo, com lock"""
        phone = lead_data.get("phone")
        if not phone:
            return await self.create_lead(lead_data)
        lock_key = f"crm:lead:{phone}"
        if not await redis_client.acquire_lock(lock_key, ttl=30):
            return {
                "success": False, "error": "lock_not_acquired",
                "message": "Operação já em andamento."
            }
        try:
            existing_lead = await self.get_lead_by_phone(phone)
            if existing_lead and existing_lead.get("id"):
                update_result = await self.update_lead(
                    existing_lead["id"], lead_data
                )
                if update_result.get("success"):
                    return {
                        "success": True, "lead_id": existing_lead["id"],
                        "message": "Lead atualizado", "created": False
                    }
                return update_result
            return await self.create_lead(lead_data)
        finally:
            await redis_client.release_lock(lock_key)

    @handle_kommo_errors()
    async def get_lead_by_phone(
            self, phone: str
    ) -> Optional[Dict[str, Any]]:
        """Busca lead REAL no Kommo por telefone com cache"""
        if not self.is_initialized:
            await self.initialize()
        clean_phone = ''.join(filter(str.isdigit, phone))
        if not clean_phone.startswith('55'):
            clean_phone = '55' + clean_phone
        cache_key = f"kommo_lead:{clean_phone}"
        cached_lead = await redis_client.get(cache_key)
        if cached_lead:
            return json.loads(cached_lead)
        try:
            await wait_for_kommo()
            async with await self._get_session() as session:
                async with session.get(
                    f"{self.base_url}/api/v4/leads",
                    headers=self.headers,
                    params={"query": clean_phone}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        leads = result.get("_embedded", {}).get("leads", [])
                        if leads:
                            lead = leads[0]
                            await redis_client.set(
                                cache_key, json.dumps(lead), ttl=300
                            )
                            return lead
                        return None
                    else:
                        error_text = await response.text()
                        raise KommoAPIException(
                            f"Erro ao buscar lead por telefone: {response.status} - "
                            f"{error_text}",
                            error_code="KOMMO_GET_LEAD_BY_PHONE_ERROR",
                            details={
                                "status_code": response.status,
                                "response": error_text
                            }
                        )
        except Exception as e:
            emoji_logger.service_error(
                f"Erro ao buscar lead por telefone {phone}: {e}"
            )
            if not isinstance(e, KommoAPIException):
                raise KommoAPIException(
                    f"Erro ao buscar lead por telefone: {e}",
                    error_code="KOMMO_GET_LEAD_BY_PHONE_EXCEPTION",
                    details={"exception": str(e)}
                )
            else:
                raise

    @handle_kommo_errors()
    async def update_lead_stage(
            self, lead_id: str, stage_name: str, notes: str = "", phone_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Atualiza o estágio de um lead no Kommo"""
        if not self.is_initialized:
            await self.initialize()
        try:
            normalized_stage = stage_name.strip().lower().replace(" ", "_")
            stage_id = self.stage_map.get(normalized_stage)
            if not stage_id:
                stage_id = self.stage_map.get(stage_name.strip()) or self.stage_map.get(stage_name.strip().upper())
                if not stage_id:
                    # Fallback para estágios configurados estaticamente
                    fallback_map = {
                        "novo_lead": settings.kommo_novo_lead_stage_id,
                        "em_qualificacao": settings.kommo_em_qualificacao_stage_id,
                        "qualificado": settings.kommo_qualificado_stage_id,
                        "desqualificado": settings.kommo_desqualificado_stage_id,
                        "atendimento_humano": settings.kommo_human_handoff_stage_id
                    }
                    stage_id = fallback_map.get(normalized_stage)
                    if stage_id:
                        emoji_logger.service_info(f"🔄 Usando stage ID configurado para '{stage_name}': {stage_id}")
                    else:
                        raise ValueError(f"Estágio '{stage_name}' não encontrado no mapa dinâmico nem nos configurados: {list(self.stage_map.keys())}")
            
            # PASSO 2 DA CORREÇÃO: Ativar pausa no Redis se for estágio de handoff
            human_handoff_stage_id = settings.kommo_human_handoff_stage_id
            if stage_id == human_handoff_stage_id and phone_number:
                await redis_client.set_human_handoff_pause(phone_number)
                emoji_logger.system_info(f"Pausa de handoff ativada para {phone_number} via CRM Service.")

            payload = [{
                "id": int(lead_id),
                "status_id": stage_id,
                "updated_at": int(datetime.now().timestamp())
            }]

            await wait_for_kommo()
            async with await self._get_session() as session:
                async with session.patch(
                    f"{self.base_url}/api/v4/leads",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        emoji_logger.team_crm(
                            f"✅ Lead {lead_id} movido para '{stage_name}'"
                        )
                        if notes:
                            await self.add_note_to_lead(lead_id, notes)
                        return {
                            "success": True,
                            "message": f"Lead movido para {stage_name}",
                            "stage_id": stage_id, "lead_id": lead_id
                        }
                    else:
                        error_text = await response.text()
                        raise KommoAPIException(
                            f"Erro ao atualizar estágio: {response.status} - {error_text}",
                            error_code="KOMMO_UPDATE_STAGE_ERROR",
                            details={
                                "status_code": response.status,
                                "response": error_text,
                                "payload_sent": payload
                            }
                        )
        except Exception as e:
            emoji_logger.service_error(
                f"Erro ao atualizar estágio do lead {lead_id}: {e}"
            )
            if not isinstance(e, KommoAPIException):
                raise KommoAPIException(
                    f"Erro ao atualizar estágio: {e}",
                    error_code="KOMMO_UPDATE_STAGE_EXCEPTION",
                    details={"exception": str(e), "lead_id": lead_id}
                )
            else:
                raise

    @async_retry_with_backoff()
    @handle_kommo_errors()
    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Busca um lead no Kommo pelo seu ID."""
        if not self.is_initialized:
            await self.initialize()
        try:
            await wait_for_kommo()
            async with await self._get_session() as session:
                async with session.get(
                    f"{self.base_url}/api/v4/leads/{lead_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return None
                    else:
                        error_text = await response.text()
                        raise KommoAPIException(
                            f"Erro ao buscar lead por ID: {response.status} - {error_text}",
                            error_code="KOMMO_GET_LEAD_BY_ID_ERROR",
                            details={"status_code": response.status, "response": error_text}
                        )
        except Exception as e:
            emoji_logger.service_error(f"Erro ao buscar lead por ID {lead_id}: {e}")
            if not isinstance(e, KommoAPIException):
                raise KommoAPIException(
                    f"Erro ao buscar lead por ID: {e}",
                    error_code="KOMMO_GET_LEAD_BY_ID_EXCEPTION",
                    details={"exception": str(e)}
                )
            else:
                raise

    async def close(self):
        """Fecha conexão com Kommo CRM"""
        self.is_initialized = False

    @async_retry_with_backoff()
    @handle_kommo_errors()
    async def add_note_to_lead(self, lead_id: str, note_text: str) -> Dict[str, Any]:
        """Adiciona uma nota a um lead no Kommo."""
        if not self.is_initialized:
            await self.initialize()
        try:
            note_payload = {
                "note_type": "common",
                "params": {
                    "text": note_text
                }
            }
            await wait_for_kommo()
            async with await self._get_session() as session:
                async with session.post(
                    f"{self.base_url}/api/v4/leads/{lead_id}/notes",
                    headers=self.headers,
                    json=[note_payload]
                ) as response:
                    if response.status == 200:
                        emoji_logger.team_crm(f"📝 Nota adicionada ao lead {lead_id}")
                        return {"success": True, "message": "Nota adicionada com sucesso."}
                    else:
                        error_text = await response.text()
                        raise KommoAPIException(
                            f"Erro ao adicionar nota: {response.status} - {error_text}",
                            error_code="KOMMO_ADD_NOTE_ERROR",
                            details={"status_code": response.status, "response": error_text}
                        )
        except Exception as e:
            emoji_logger.service_error(f"Erro ao adicionar nota ao lead {lead_id}: {e}")
            if not isinstance(e, KommoAPIException):
                raise KommoAPIException(
                    f"Erro ao adicionar nota: {e}",
                    error_code="KOMMO_ADD_NOTE_EXCEPTION",
                    details={"exception": str(e), "lead_id": lead_id}
                )
            else:
                raise
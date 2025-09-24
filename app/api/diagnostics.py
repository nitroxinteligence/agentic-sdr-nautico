"""
Diagnostics API - Endpoints para diagnóstico detalhado do sistema
"""
from fastapi import APIRouter
from datetime import datetime
import asyncio
import psutil
import sys
from loguru import logger

from app.integrations.supabase_client import supabase_client
from app.integrations.evolution import evolution_client
from app.integrations.redis_client import redis_client
from app.config import settings
from app.utils.logger import emoji_logger
from app.services.kommo_queue_service import kommo_queue_service

router = APIRouter()


@router.get("/system")
async def system_diagnostics():
    """Diagnóstico completo do sistema"""
    try:
        # Informações do sistema
        process = psutil.Process()
        memory_info = process.memory_info()
        
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "process_id": process.pid,
            "uptime_seconds": (datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds(),
            "memory": {
                "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                "percent": process.memory_percent()
            },
            "cpu_percent": process.cpu_percent(),
            "threads": process.num_threads(),
            "open_files": len(process.open_files())
        }
        
        # Status dos serviços
        services_status = {}
        
        # Redis
        try:
            redis_connected = await redis_client.ping()
            redis_info = await redis_client.info() if redis_connected else {}
            services_status["redis"] = {
                "status": "connected" if redis_connected else "disconnected",
                "version": redis_info.get("redis_version", "unknown"),
                "memory_used": redis_info.get("used_memory_human", "unknown"),
                "connected_clients": redis_info.get("connected_clients", 0),
                "uptime_seconds": redis_info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            services_status["redis"] = {
                "status": "error",
                "error": str(e)
            }
            
        # Supabase
        try:
            supabase_connected = await supabase_client.test_connection()
            services_status["supabase"] = {
                "status": "connected" if supabase_connected else "disconnected",
                "url": settings.supabase_url[:50] + "..." if settings.supabase_url else "not_configured"
            }
        except Exception as e:
            services_status["supabase"] = {
                "status": "error", 
                "error": str(e)
            }
            
        # Evolution API
        try:
            evolution_connected = await evolution_client.test_connection()
            services_status["evolution"] = {
                "status": "connected" if evolution_connected else "disconnected",
                "url": settings.evolution_api_url[:50] + "..." if settings.evolution_api_url else "not_configured",
                "instance": settings.evolution_instance_name
            }
        except Exception as e:
            services_status["evolution"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Configurações importantes
        config_check = {
            "environment": settings.environment,
            "debug": settings.debug,
            "redis_enabled": settings.enable_redis,
            "followup_enabled": settings.enable_follow_up_automation,
            "kommo_enabled": settings.enable_kommo_crm,
            "evolution_enabled": settings.enable_evolution_api,
            "supabase_enabled": settings.enable_supabase
        }
        
        # Status geral
        all_services_ok = all(
            service.get("status") == "connected" 
            for service in services_status.values()
        )
        
        return {
            "overall_status": "healthy" if all_services_ok else "degraded",
            "system": system_info,
            "services": services_status,
            "configuration": config_check,
            "recommendations": generate_recommendations(services_status, system_info)
        }
        
    except Exception as e:
        logger.error(f"Erro no diagnóstico do sistema: {e}")
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/connections")
async def test_all_connections():
    """Testa todas as conexões de serviços"""
    results = {}
    
    # Teste Redis
    try:
        start_time = datetime.now()
        redis_connected = await redis_client.ping()
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds() * 1000
        
        results["redis"] = {
            "connected": redis_connected,
            "latency_ms": round(latency, 2),
            "url": settings.redis_url
        }
    except Exception as e:
        results["redis"] = {
            "connected": False,
            "error": str(e)
        }
    
    # Teste Supabase
    try:
        start_time = datetime.now()
        supabase_connected = await supabase_client.test_connection()
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds() * 1000
        
        results["supabase"] = {
            "connected": supabase_connected,
            "latency_ms": round(latency, 2),
            "url": settings.supabase_url[:50] + "..."
        }
    except Exception as e:
        results["supabase"] = {
            "connected": False,
            "error": str(e)
        }
    
    # Teste Evolution API
    try:
        start_time = datetime.now()
        evolution_connected = await evolution_client.test_connection()
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds() * 1000
        
        results["evolution"] = {
            "connected": evolution_connected,
            "latency_ms": round(latency, 2),
            "url": settings.evolution_api_url[:50] + "...",
            "instance": settings.evolution_instance_name
        }
    except Exception as e:
        results["evolution"] = {
            "connected": False,
            "error": str(e)
        }
    
    # Status geral
    all_connected = all(result.get("connected", False) for result in results.values())
    
    return {
        "all_connected": all_connected,
        "timestamp": datetime.now().isoformat(),
        "connections": results
    }


@router.get("/logs/recent")
async def get_recent_logs():
    """Retorna logs recentes do sistema"""
    try:
        # Buscar logs recentes do Redis se disponível
        recent_events = []
        
        if await redis_client.ping():
            # Buscar eventos recentes do cache
            try:
                events = await redis_client.lrange("system_events", 0, 49)  # Últimos 50 eventos
                recent_events = events if events else []
            except:
                pass
        
        return {
            "recent_events": recent_events,
            "timestamp": datetime.now().isoformat(),
            "note": "Logs completos disponíveis nos logs do container"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def generate_recommendations(services_status, system_info):
    """Gera recomendações baseadas no status dos serviços"""
    recommendations = []
    
    # Verificar memória
    memory_percent = system_info["memory"]["percent"]
    if memory_percent > 80:
        recommendations.append({
            "type": "warning",
            "message": f"Alto uso de memória ({memory_percent:.1f}%). Considere aumentar recursos.",
            "action": "scale_memory"
        })
    
    # Verificar serviços
    for service_name, service_info in services_status.items():
        if service_info.get("status") != "connected":
            recommendations.append({
                "type": "error",
                "message": f"Serviço {service_name} desconectado: {service_info.get('error', 'Conexão falhou')}",
                "action": f"check_{service_name}_config"
            })
    
    # Verificar Redis específico
    redis_info = services_status.get("redis", {})
    if redis_info.get("connected_clients", 0) > 50:
        recommendations.append({
            "type": "warning", 
            "message": f"Muitas conexões Redis ({redis_info.get('connected_clients')}). Verificar vazamentos de conexão.",
            "action": "monitor_redis_connections"
        })
    
    return recommendations


@router.post("/fix/connections")
async def fix_connections():
    """Tenta reconectar todos os serviços"""
    results = {}
    
    # Reconectar Redis
    try:
        await redis_client.connect()
        redis_ok = await redis_client.ping()
        results["redis"] = {
            "reconnected": redis_ok,
            "message": "Reconectado com sucesso" if redis_ok else "Falha na reconexão"
        }
    except Exception as e:
        results["redis"] = {
            "reconnected": False,
            "error": str(e)
        }
    
    # Reconectar Evolution (se necessário)
    try:
        evolution_ok = await evolution_client.test_connection()
        results["evolution"] = {
            "reconnected": evolution_ok,
            "message": "Conexão OK" if evolution_ok else "Falha na conexão"
        }
    except Exception as e:
        results["evolution"] = {
            "reconnected": False,
            "error": str(e)
        }
    
    return {
        "timestamp": datetime.now().isoformat(),
        "fixes_applied": results
    }


@router.get("/kommo-queue")
async def kommo_queue_status():
    """Status detalhado da fila do Kommo CRM"""
    try:
        stats = kommo_queue_service.get_queue_stats()

        # Adicionar informações extras
        status_info = {
            "queue_stats": stats,
            "service_status": {
                "processing": kommo_queue_service.processing,
                "initialized": kommo_queue_service.crm_service.is_initialized if kommo_queue_service.crm_service else False,
                "max_requests_per_second": kommo_queue_service.max_requests_per_second
            },
            "rate_limit_info": {
                "blocked_until": kommo_queue_service.blocked_until,
                "consecutive_429_errors": kommo_queue_service.consecutive_429_errors,
                "consecutive_403_errors": kommo_queue_service.consecutive_403_errors
            },
            "timestamp": datetime.now().isoformat()
        }

        # Classificar status geral
        if stats.get("consecutive_403_errors", 0) > 0:
            status_info["overall_status"] = "IP_BLOCKED"
            status_info["status_message"] = "IP bloqueado pela API do Kommo"
        elif stats.get("consecutive_429_errors", 0) > 2:
            status_info["overall_status"] = "RATE_LIMITED"
            status_info["status_message"] = "Rate limit ativo"
        elif stats.get("queue_size", 0) > 10:
            status_info["overall_status"] = "BUSY"
            status_info["status_message"] = f"Fila com {stats.get('queue_size')} operações pendentes"
        else:
            status_info["overall_status"] = "HEALTHY"
            status_info["status_message"] = "Sistema funcionando normalmente"

        return status_info

    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "overall_status": "ERROR"
        }


@router.post("/kommo-queue/test")
async def test_kommo_queue():
    """Testa a fila do Kommo com operações simuladas"""
    try:
        # Teste simples de criação de lead
        test_result = await kommo_queue_service.create_lead({
            "name": "Teste API Queue",
            "phone": f"5511999{int(datetime.now().timestamp()) % 100000:05d}",
            "bill_value": 100.00
        })

        return {
            "test_successful": test_result.get("success", False),
            "result": test_result,
            "timestamp": datetime.now().isoformat(),
            "queue_stats": kommo_queue_service.get_queue_stats()
        }

    except Exception as e:
        return {
            "test_successful": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
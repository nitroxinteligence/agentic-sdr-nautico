#!/usr/bin/env python3
"""
Script para remover a entrada de rate limiting remanescente
"""
import asyncio
import redis.asyncio as redis
import os
import sys

# Adicionar o path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings


async def remove_specific_entries():
    """Remove especificamente as entradas com 238443732942898"""
    
    print("🎯 Removendo entradas específicas com número problemático...")
    
    try:
        redis_url = settings.get_redis_url()
        redis_client = await redis.from_url(
            redis_url,
            encoding="utf-8", 
            decode_responses=True
        )
        
        await redis_client.ping()
        print("✅ Conectado ao Redis!")
        
        # Entradas específicas para remover
        specific_keys = [
            "rate:message:238443732942898@lid",
            "conversation:238443732942898@lid",  # Caso não tenha sido removida
            "message:238443732942898@lid",
            "238443732942898@lid",
            "rate_limit:message:238443732942898",
            "message:238443732942898"
        ]
        
        removed = 0
        
        for key in specific_keys:
            try:
                # Verificar se existe
                if await redis_client.exists(key):
                    value = await redis_client.get(key)
                    print(f"🎯 Removendo: {key} -> {value}")
                    
                    # Remover
                    await redis_client.delete(key)
                    print(f"✅ REMOVIDO: {key}")
                    removed += 1
                else:
                    print(f"⚪ Não existe: {key}")
                    
            except Exception as e:
                print(f"❌ Erro ao processar {key}: {e}")
        
        # Buscar qualquer coisa que contenha o número problemático
        print(f"\n🔍 Busca final por qualquer entrada com 238443732942898...")
        
        try:
            all_keys = await redis_client.keys("*238443732942898*")
            
            if all_keys:
                print(f"🚨 Ainda existem {len(all_keys)} entradas:")
                for key in all_keys:
                    value = await redis_client.get(key)
                    print(f"   🎯 {key} -> {value}")
                    
                    # Remover todas
                    await redis_client.delete(key)
                    print(f"   ✅ FORÇADO REMOÇÃO: {key}")
                    removed += 1
            else:
                print("✅ Nenhuma entrada restante encontrada!")
                
        except Exception as e:
            print(f"❌ Erro na busca final: {e}")
        
        await redis_client.aclose()
        
        print(f"\n📊 TOTAL REMOVIDO: {removed} entradas")
        return removed
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 0


async def main():
    """Função principal"""
    
    print("🎯 Remoção Específica do Cache Problemático")
    print("=" * 50)
    
    removed = await remove_specific_entries()
    
    if removed > 0:
        print(f"\n✅ Cache limpo: {removed} entradas problemáticas removidas")
        print(f"🚀 TESTE AGORA: Envie uma mensagem no WhatsApp!")
    else:
        print(f"\n🤔 Nenhuma entrada problemática encontrada")
        print(f"   Pode estar tudo limpo agora")
    
    print("=" * 50)
    print("🏁 Limpeza específica finalizada")


if __name__ == "__main__":
    asyncio.run(main())
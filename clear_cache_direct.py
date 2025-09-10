#!/usr/bin/env python3
"""
Script para limpar cache Redis usando conexão direta
Alternativa caso o cliente personalizado não funcione
"""
import asyncio
import redis.asyncio as redis
import os
import sys

# Adicionar o path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings


async def clear_cache_direct():
    """Limpa cache usando conexão direta ao Redis"""
    
    print("🔧 Conectando diretamente ao Redis...")
    
    try:
        # Obter URL do Redis das configurações
        redis_url = settings.get_redis_url()
        print(f"🔗 URL Redis: {redis_url[:20]}...")
        
        # Conectar diretamente
        redis_client = await redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Testar conexão
        await redis_client.ping()
        print("✅ Conectado ao Redis!")
        
        # Buscar chaves problemáticas
        patterns_to_check = [
            "pushname_phone:*",
            "*238443732942898*", 
            "message:*",
            "rate_limit:*",
            "*unknown_*"
        ]
        
        total_cleared = 0
        
        for pattern in patterns_to_check:
            print(f"\n🔍 Buscando padrão: {pattern}")
            
            try:
                keys = await redis_client.keys(pattern)
                
                if keys:
                    print(f"   Encontradas {len(keys)} chaves:")
                    
                    for key in keys:
                        try:
                            # Obter valor
                            value = await redis_client.get(key)
                            print(f"   📋 {key} -> {value}")
                            
                            # Verificar se é problemático
                            is_problematic = False
                            if value:
                                value_str = str(value)
                                if ('238443732942898' in value_str or 
                                    'unknown_' in value_str or 
                                    len(value_str) > 20):  # Números muito longos
                                    is_problematic = True
                            
                            if is_problematic:
                                await redis_client.delete(key)
                                print(f"   ✅ REMOVIDO: {key}")
                                total_cleared += 1
                            else:
                                print(f"   ℹ️  MANTIDO: {key}")
                                
                        except Exception as e:
                            print(f"   ❌ Erro ao processar {key}: {e}")
                else:
                    print(f"   ✅ Nenhuma chave encontrada para {pattern}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao buscar padrão {pattern}: {e}")
        
        print(f"\n📊 TOTAL REMOVIDO: {total_cleared} entradas")
        
        # Fechar conexão
        await redis_client.close()
        
        return total_cleared
        
    except Exception as e:
        print(f"❌ Erro na conexão direta: {e}")
        return 0


async def flush_redis_completely():
    """Limpa completamente o Redis"""
    
    print("\n🚨 FLUSH COMPLETO DO REDIS")
    confirm = input("⚠️  CUIDADO: Isso vai apagar TUDO do Redis!\n   Digite 'CONFIRMO' para continuar: ")
    
    if confirm != 'CONFIRMO':
        print("❌ Flush cancelado")
        return False
    
    try:
        redis_url = settings.get_redis_url()
        redis_client = await redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        
        # Flush do banco atual
        await redis_client.flushdb()
        print("✅ Redis completamente limpo!")
        
        await redis_client.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no flush: {e}")
        return False


async def main():
    """Função principal"""
    
    print("🔧 Limpeza Direta do Cache Redis")
    print("=" * 50)
    
    try:
        # Tentar limpeza seletiva primeiro
        cleared = await clear_cache_direct()
        
        if cleared > 0:
            print(f"\n✅ Cache limpo: {cleared} entradas removidas")
            print(f"   Agora teste enviando uma mensagem!")
        else:
            print(f"\n🤔 Nenhuma entrada problemática encontrada")
            
            # Oferecer flush completo
            if input("\n🚨 Tentar FLUSH COMPLETO? (y/N): ").lower() == 'y':
                if await flush_redis_completely():
                    print("✅ Cache completamente resetado!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        
        # Última opção: flush completo em caso de erro
        if input(f"\n🚨 Erro no acesso. Tentar FLUSH COMPLETO mesmo assim? (y/N): ").lower() == 'y':
            await flush_redis_completely()
    
    print("=" * 50)
    print("🏁 Limpeza finalizada")


if __name__ == "__main__":
    asyncio.run(main())
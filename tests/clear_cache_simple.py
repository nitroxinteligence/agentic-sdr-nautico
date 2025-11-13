#!/usr/bin/env python3
"""
Script simplificado para limpar cache Redis problemático
Funciona com o RedisClient personalizado do projeto
"""
import asyncio
import os
import sys

# Adicionar o path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.integrations.redis_client import redis_client
from app.utils.logger import emoji_logger


async def clear_known_problematic_entries():
    """
    Limpa entradas conhecidas que podem estar causando o problema
    Como não temos acesso ao método keys(), vamos tentar chaves específicas
    """
    
    print("🧹 Limpando entradas conhecidas do cache...")
    
    # Conectar se necessário
    if not await redis_client.is_connected():
        await redis_client.connect()
    
    # Lista de possíveis chaves problemáticas baseadas nos logs
    possible_keys = [
        # Associações pushName -> telefone
        "pushname_phone:Elizângela",
        "pushname_phone:Elizângela Dos Santos Silva", 
        "pushname_phone:Petrus",
        "pushname_phone:Luciano",
        "pushname_phone:Teste",
        "pushname_phone:Teste De Envio",
        
        # Rate limits do número problemático
        "message:238443732942898",
        "rate_limit:message:238443732942898",
        "rate_limit:238443732942898",
        
        # Possíveis variações do seu nome (substitua se souber)
        "pushname_phone:Seu Nome",
        "pushname_phone:Usuario",
        "pushname_phone:User",
        
        # Cache de conversas
        "conversation:238443732942898",
        "lead:238443732942898",
        
        # Chaves que podem estar associadas ao @lid
        "238443732942898@lid",
        "conversation_id:238443732942898",
        "lead_id:238443732942898"
    ]
    
    cleared_count = 0
    found_count = 0
    
    print(f"🔍 Verificando {len(possible_keys)} possíveis chaves problemáticas...\n")
    
    for key in possible_keys:
        try:
            # Verificar se a chave existe
            if await redis_client.exists(key):
                # Obter o valor para mostrar
                value = await redis_client.get(key)
                print(f"🚨 ENCONTRADO: '{key}' -> '{value}'")
                found_count += 1
                
                # Verificar se contém dados problemáticos
                if value and ('238443732942898' in str(value) or 'unknown_' in str(value)):
                    # Deletar a chave
                    if await redis_client.delete(key):
                        print(f"✅ REMOVIDO: '{key}'")
                        cleared_count += 1
                    else:
                        print(f"❌ ERRO ao remover: '{key}'")
                else:
                    print(f"ℹ️  MANTIDO (parece válido): '{key}' -> '{value}'")
            else:
                print(f"⚪ Chave não existe: '{key}'")
                
        except Exception as e:
            print(f"❌ Erro ao verificar '{key}': {e}")
    
    print(f"\n📊 RESUMO:")
    print(f"   Chaves encontradas: {found_count}")
    print(f"   Chaves removidas: {cleared_count}")
    
    return cleared_count


async def test_direct_redis_access():
    """Tenta acessar diretamente o cliente Redis interno para usar keys()"""
    
    print("\n🔧 Tentando acesso direto ao Redis...")
    
    try:
        # Conectar se necessário
        if not await redis_client.is_connected():
            await redis_client.connect()
        
        # Acessar cliente interno diretamente
        if hasattr(redis_client, 'redis_client') and redis_client.redis_client:
            internal_client = redis_client.redis_client
            
            # Tentar usar keys() no cliente interno
            try:
                print("🔍 Buscando chaves com padrão 'pushname_phone:*'...")
                keys = await internal_client.keys("pushname_phone:*")
                
                if keys:
                    print(f"✅ Encontradas {len(keys)} chaves pushname_phone:")
                    
                    cleared = 0
                    for key in keys:
                        if isinstance(key, bytes):
                            key = key.decode('utf-8')
                        
                        # Obter valor
                        value = await redis_client.get(key)
                        print(f"   📋 {key} -> {value}")
                        
                        # Se contém número problemático, deletar
                        if value and ('238443732942898' in str(value) or 'unknown_' in str(value) or len(str(value)) > 15):
                            if await redis_client.delete(key):
                                print(f"   ✅ REMOVIDO: {key}")
                                cleared += 1
                    
                    print(f"\n✅ Limpeza direta: {cleared} entradas removidas")
                    return cleared
                else:
                    print("ℹ️  Nenhuma chave pushname_phone encontrada")
                    
            except Exception as e:
                print(f"❌ Erro ao usar keys() diretamente: {e}")
                return 0
        else:
            print("❌ Cliente Redis interno não disponível")
            return 0
            
    except Exception as e:
        print(f"❌ Erro no acesso direto: {e}")
        return 0


async def flush_all_cache():
    """Opção drástica: limpar TODO o cache (use com cuidado!)"""
    
    print("\n🚨 OPÇÃO DRÁSTICA: Limpar TODO o cache")
    
    confirm = input("⚠️  ATENÇÃO: Isso vai limpar TODAS as entradas do cache!\n   Digite 'FLUSH' para confirmar ou qualquer coisa para cancelar: ")
    
    if confirm == 'FLUSH':
        try:
            if not await redis_client.is_connected():
                await redis_client.connect()
            
            # Tentar flush all no cliente interno
            if hasattr(redis_client, 'redis_client') and redis_client.redis_client:
                await redis_client.redis_client.flushdb()
                print("✅ Cache completamente limpo!")
                return True
            else:
                print("❌ Não foi possível acessar função flush")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao limpar cache: {e}")
            return False
    else:
        print("❌ Flush cancelado")
        return False


async def main():
    """Função principal"""
    
    print("🧹 Script de Limpeza de Cache Redis (Versão Corrigida)")
    print("=" * 60)
    
    try:
        # Método 1: Tentar chaves conhecidas
        cleared1 = await clear_known_problematic_entries()
        
        # Método 2: Tentar acesso direto
        cleared2 = await test_direct_redis_access()
        
        total_cleared = cleared1 + cleared2
        
        print(f"\n" + "=" * 60)
        print(f"📊 RESULTADO FINAL:")
        print(f"   Total de entradas removidas: {total_cleared}")
        
        if total_cleared > 0:
            print(f"\n✅ Cache limpo! Teste enviando uma mensagem agora.")
        else:
            print(f"\n🤔 Nenhuma entrada problemática encontrada no cache.")
            print(f"   Opções:")
            print(f"   1. O problema pode estar em outra parte")
            print(f"   2. Use a opção de flush completo (cuidado!)")
            
            # Oferecer opção de flush
            if input("\n🚨 Deseja tentar FLUSH COMPLETO do cache? (y/N): ").lower() == 'y':
                await flush_all_cache()
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    finally:
        # Fechar conexão
        try:
            await redis_client.disconnect()
        except:
            pass
    
    print("=" * 60)
    print("🏁 Script finalizado")


if __name__ == "__main__":
    asyncio.run(main())
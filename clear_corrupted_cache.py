#!/usr/bin/env python3
"""
Script para limpar cache corrompido que está associando números inválidos
Execute este script para limpar associações incorretas pushName -> telefone
"""
import asyncio
import os
import sys
from typing import List, Dict, Set

# Adicionar o path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.integrations.redis_client import redis_client
from app.integrations.supabase_client import supabase_client
from app.utils.logger import emoji_logger


def validate_phone_number(phone: str) -> bool:
    """Valida se um número de telefone é válido"""
    if not phone:
        return False
    
    digits_only = ''.join(filter(str.isdigit, phone))
    
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False
    
    if len(set(digits_only)) < 3:
        return False
    
    if digits_only.startswith('55') and len(digits_only) < 12:
        return False
    
    return True


async def find_corrupted_cache_keys() -> List[str]:
    """Encontra chaves do cache com números inválidos"""
    corrupted_keys = []
    
    try:
        # Buscar todas as chaves pushname_phone
        pattern = "pushname_phone:*"
        keys = await redis_client.keys(pattern)
        
        print(f"🔍 Verificando {len(keys)} entradas no cache...")
        
        for key in keys:
            try:
                # Decodificar a chave se necessário
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                
                # Obter valor associado
                phone = await redis_client.get(key)
                if isinstance(phone, bytes):
                    phone = phone.decode('utf-8')
                
                # Verificar se o telefone é inválido
                if phone and not validate_phone_number(phone):
                    pushname = key.replace("pushname_phone:", "")
                    print(f"❌ Cache corrompido: '{pushname}' -> '{phone}'")
                    corrupted_keys.append(key)
                elif phone:
                    pushname = key.replace("pushname_phone:", "")
                    print(f"✅ Cache válido: '{pushname}' -> '{phone}'")
                
            except Exception as e:
                print(f"⚠️  Erro ao verificar chave {key}: {e}")
                
    except Exception as e:
        print(f"❌ Erro ao buscar chaves do Redis: {e}")
        emoji_logger.system_error("ClearCache", f"Erro ao acessar Redis: {e}")
    
    return corrupted_keys


async def find_corrupted_leads_and_conversations() -> Dict[str, List]:
    """Encontra leads e conversas com números inválidos"""
    results = {
        "leads": [],
        "conversations": [],
        "follow_ups": []
    }
    
    try:
        # Verificar leads
        leads_result = supabase_client.client.table('leads').select('*').execute()
        for lead in leads_result.data:
            phone = lead.get('phone_number', '')
            if phone and not validate_phone_number(phone):
                results["leads"].append(lead)
                print(f"🎯 Lead com número inválido: {lead.get('name', 'Sem nome')} -> '{phone}'")
        
        # Verificar conversas
        conversations_result = supabase_client.client.table('conversations').select('*').execute()
        for conv in conversations_result.data:
            phone = conv.get('phone_number', '')
            if phone and not validate_phone_number(phone):
                results["conversations"].append(conv)
                print(f"💬 Conversa com número inválido: '{phone}' -> ID: {conv.get('id')}")
        
        # Verificar follow-ups
        followups_result = supabase_client.client.table('follow_ups').select('*').execute()
        for followup in followups_result.data:
            phone = followup.get('phone_number', '')
            if phone and not validate_phone_number(phone):
                results["follow_ups"].append(followup)
                print(f"📅 Follow-up com número inválido: '{phone}' -> Status: {followup.get('status')}")
                
    except Exception as e:
        print(f"❌ Erro ao buscar dados do Supabase: {e}")
        emoji_logger.system_error("ClearCache", f"Erro ao acessar Supabase: {e}")
    
    return results


async def clear_corrupted_cache(corrupted_keys: List[str], dry_run: bool = True) -> int:
    """Limpa chaves corrompidas do cache"""
    cleared = 0
    
    for key in corrupted_keys:
        print(f"🧹 {'[DRY-RUN] ' if dry_run else ''}Limpando cache: {key}")
        
        if not dry_run:
            try:
                await redis_client.delete(key)
                cleared += 1
                emoji_logger.system_success(f"Cache limpo: {key}")
            except Exception as e:
                print(f"❌ Erro ao limpar {key}: {e}")
    
    return cleared


async def fix_specific_number_issue():
    """Limpa especificamente o problema do número 238443732942898"""
    problematic_number = "238443732942898"
    
    print(f"\n🎯 Verificando associações específicas com '{problematic_number}':")
    
    # Verificar no cache Redis
    try:
        pattern = "pushname_phone:*"
        keys = await redis_client.keys(pattern)
        
        problematic_keys = []
        for key in keys:
            if isinstance(key, bytes):
                key = key.decode('utf-8')
            
            phone = await redis_client.get(key)
            if isinstance(phone, bytes):
                phone = phone.decode('utf-8')
            
            if problematic_number in str(phone):
                pushname = key.replace("pushname_phone:", "")
                print(f"🚨 ENCONTRADO: pushName '{pushname}' -> '{phone}'")
                problematic_keys.append(key)
        
        if problematic_keys:
            print(f"\n🧹 Encontradas {len(problematic_keys)} associações com número problemático")
            return problematic_keys
        else:
            print("✅ Nenhuma associação encontrada no cache com esse número")
            return []
            
    except Exception as e:
        print(f"❌ Erro ao verificar associações: {e}")
        return []


async def main():
    """Função principal"""
    print("🧹 Script de Limpeza de Cache Corrompido")
    print("=" * 60)
    
    dry_run = '--execute' not in sys.argv
    
    if dry_run:
        print("⚠️  MODO DRY-RUN: Apenas identificando problemas")
        print("   Para executar as correções, use: python clear_corrupted_cache.py --execute")
    else:
        print("🚨 MODO EXECUÇÃO: Alterações serão feitas!")
        confirm = input("Tem certeza que deseja continuar? (digite 'SIM' para confirmar): ")
        if confirm != 'SIM':
            print("❌ Operação cancelada pelo usuário")
            return
    
    # Verificar problema específico primeiro
    print("\n🎯 VERIFICAÇÃO ESPECÍFICA DO NÚMERO PROBLEMÁTICO:")
    problematic_keys = await fix_specific_number_issue()
    
    # Análise geral
    print("\n🔍 ANÁLISE GERAL DO CACHE:")
    corrupted_keys = await find_corrupted_cache_keys()
    
    print(f"\n🔍 ANÁLISE DOS DADOS PERSISTIDOS:")
    corrupted_data = await find_corrupted_leads_and_conversations()
    
    # Resumo
    print(f"\n📊 RESUMO:")
    print(f"   Entradas corrompidas no cache: {len(corrupted_keys)}")
    print(f"   Leads com números inválidos: {len(corrupted_data['leads'])}")
    print(f"   Conversas com números inválidos: {len(corrupted_data['conversations'])}")
    print(f"   Follow-ups com números inválidos: {len(corrupted_data['follow_ups'])}")
    print(f"   Associações com número problemático: {len(problematic_keys)}")
    
    # Executar limpeza
    if not dry_run and (corrupted_keys or problematic_keys):
        print(f"\n🚀 Iniciando limpeza do cache...")
        
        all_keys_to_clear = list(set(corrupted_keys + problematic_keys))
        cleared = await clear_corrupted_cache(all_keys_to_clear, dry_run=False)
        
        print(f"\n✅ Limpeza do cache concluída:")
        print(f"   Entradas removidas: {cleared}")
        print(f"\n💡 IMPORTANTE: Para limpar os dados persistidos, execute:")
        print(f"   python cleanup_invalid_data.py --execute")
    
    elif dry_run:
        print(f"\n💡 Para executar a limpeza, rode:")
        print(f"   python clear_corrupted_cache.py --execute")
    
    print(f"\n" + "=" * 60)
    print("🏁 Análise concluída")


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Script de limpeza imediata para resolver os números inválidos
FOCO: Limpar dados corrompidos do banco (que é a causa raiz)
"""
import asyncio
import os
import sys
from datetime import datetime

# Adicionar o path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.integrations.supabase_client import supabase_client
from app.utils.logger import emoji_logger


def validate_phone_number(phone: str) -> bool:
    """Valida se um número de telefone é válido"""
    if not phone:
        return False
    
    # Números que começam com 'unknown_' são definitivamente inválidos
    if phone.startswith('unknown_'):
        return False
    
    digits_only = ''.join(filter(str.isdigit, phone))
    
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False
    
    if len(set(digits_only)) < 3:
        return False
    
    if digits_only.startswith('55') and len(digits_only) < 12:
        return False
    
    return True


async def find_and_clean_invalid_leads(dry_run: bool = True):
    """Encontra e limpa leads com números inválidos"""
    
    print("🔍 Buscando leads com números inválidos...")
    
    try:
        # Buscar todos os leads
        result = supabase_client.client.table('leads').select('*').execute()
        leads = result.data
        
        invalid_leads = []
        for lead in leads:
            phone = lead.get('phone_number', '')
            if phone and not validate_phone_number(phone):
                invalid_leads.append(lead)
                name = lead.get('name', 'Sem nome')
                print(f"❌ Lead inválido: {name} -> '{phone}' (ID: {lead['id']})")
        
        print(f"\n📊 Encontrados {len(invalid_leads)} leads com números inválidos")
        
        if invalid_leads and not dry_run:
            print("🧹 Iniciando limpeza...")
            
            cleaned = 0
            for lead in invalid_leads:
                try:
                    # DELETAR o lead completamente (números unknown são lixo)
                    supabase_client.client.table('leads').delete().eq('id', lead['id']).execute()
                    print(f"✅ Lead deletado: {lead.get('name', 'Sem nome')} (ID: {lead['id']})")
                    cleaned += 1
                except Exception as e:
                    print(f"❌ Erro ao deletar lead {lead['id']}: {e}")
            
            print(f"\n✅ Limpeza concluída: {cleaned} leads removidos")
        
        return len(invalid_leads)
        
    except Exception as e:
        print(f"❌ Erro ao processar leads: {e}")
        return 0


async def find_and_clean_invalid_conversations(dry_run: bool = True):
    """Encontra e limpa conversas com números inválidos"""
    
    print("\n🔍 Buscando conversas com números inválidos...")
    
    try:
        # Buscar todas as conversas
        result = supabase_client.client.table('conversations').select('*').execute()
        conversations = result.data
        
        invalid_conversations = []
        for conv in conversations:
            phone = conv.get('phone_number', '')
            if phone and not validate_phone_number(phone):
                invalid_conversations.append(conv)
                print(f"❌ Conversa inválida: '{phone}' (ID: {conv['id']})")
        
        print(f"\n📊 Encontradas {len(invalid_conversations)} conversas com números inválidos")
        
        if invalid_conversations and not dry_run:
            print("🧹 Iniciando limpeza...")
            
            cleaned = 0
            for conv in invalid_conversations:
                try:
                    # DELETAR a conversa completamente
                    supabase_client.client.table('conversations').delete().eq('id', conv['id']).execute()
                    print(f"✅ Conversa deletada: {conv['phone_number']} (ID: {conv['id']})")
                    cleaned += 1
                except Exception as e:
                    print(f"❌ Erro ao deletar conversa {conv['id']}: {e}")
            
            print(f"\n✅ Limpeza concluída: {cleaned} conversas removidas")
        
        return len(invalid_conversations)
        
    except Exception as e:
        print(f"❌ Erro ao processar conversas: {e}")
        return 0


async def find_and_clean_invalid_followups(dry_run: bool = True):
    """Encontra e limpa follow-ups com números inválidos"""
    
    print("\n🔍 Buscando follow-ups com números inválidos...")
    
    try:
        # Buscar todos os follow-ups
        result = supabase_client.client.table('follow_ups').select('*').execute()
        followups = result.data
        
        invalid_followups = []
        for followup in followups:
            phone = followup.get('phone_number', '')
            if phone and not validate_phone_number(phone):
                invalid_followups.append(followup)
                status = followup.get('status', 'unknown')
                print(f"❌ Follow-up inválido: '{phone}' -> Status: {status} (ID: {followup['id']})")
        
        print(f"\n📊 Encontrados {len(invalid_followups)} follow-ups com números inválidos")
        
        if invalid_followups and not dry_run:
            print("🧹 Iniciando limpeza...")
            
            cleaned = 0
            for followup in invalid_followups:
                try:
                    if followup.get('status') in ['pending', 'queued']:
                        # Cancelar follow-ups pendentes
                        supabase_client.client.table('follow_ups').update({
                            'status': 'cancelled',
                            'error_reason': f"Número inválido removido: {followup.get('phone_number')}",
                            'updated_at': datetime.now().isoformat()
                        }).eq('id', followup['id']).execute()
                        print(f"✅ Follow-up cancelado: {followup['id']}")
                    else:
                        # Deletar follow-ups já processados
                        supabase_client.client.table('follow_ups').delete().eq('id', followup['id']).execute()
                        print(f"✅ Follow-up deletado: {followup['id']}")
                    
                    cleaned += 1
                except Exception as e:
                    print(f"❌ Erro ao limpar follow-up {followup['id']}: {e}")
            
            print(f"\n✅ Limpeza concluída: {cleaned} follow-ups processados")
        
        return len(invalid_followups)
        
    except Exception as e:
        print(f"❌ Erro ao processar follow-ups: {e}")
        return 0


async def search_specific_number():
    """Busca especificamente pelo número problemático 238443732942898"""
    
    print("\n🎯 BUSCA ESPECÍFICA PELO NÚMERO 238443732942898:")
    
    found_items = []
    
    try:
        # Buscar em leads
        result = supabase_client.client.table('leads').select('*').execute()
        for lead in result.data:
            phone = lead.get('phone_number', '')
            if '238443732942898' in str(phone):
                print(f"🚨 ENCONTRADO EM LEADS: {lead.get('name')} -> '{phone}' (ID: {lead['id']})")
                found_items.append(('leads', lead['id'], phone))
        
        # Buscar em conversations
        result = supabase_client.client.table('conversations').select('*').execute()
        for conv in result.data:
            phone = conv.get('phone_number', '')
            if '238443732942898' in str(phone):
                print(f"🚨 ENCONTRADO EM CONVERSATIONS: '{phone}' (ID: {conv['id']})")
                found_items.append(('conversations', conv['id'], phone))
        
        # Buscar em follow_ups
        result = supabase_client.client.table('follow_ups').select('*').execute()
        for followup in result.data:
            phone = followup.get('phone_number', '')
            if '238443732942898' in str(phone):
                print(f"🚨 ENCONTRADO EM FOLLOW_UPS: '{phone}' -> Status: {followup.get('status')} (ID: {followup['id']})")
                found_items.append(('follow_ups', followup['id'], phone))
        
        if not found_items:
            print("✅ Número problemático 238443732942898 NÃO encontrado no banco!")
        else:
            print(f"\n🚨 TOTAL: {len(found_items)} ocorrências do número problemático encontradas")
        
        return found_items
        
    except Exception as e:
        print(f"❌ Erro na busca específica: {e}")
        return []


async def main():
    """Função principal de limpeza imediata"""
    
    print("🚨 LIMPEZA IMEDIATA DE DADOS CORROMPIDOS")
    print("=" * 60)
    
    # Verificar se é dry-run ou execução real
    dry_run = '--execute' not in sys.argv
    
    if dry_run:
        print("⚠️  MODO ANÁLISE: Identificando problemas sem fazer alterações")
        print("   Para executar as correções, use: python immediate_cleanup.py --execute")
    else:
        print("🚨 MODO EXECUÇÃO: DADOS SERÃO DELETADOS!")
        confirm = input("Tem certeza que deseja continuar? (digite 'SIM' para confirmar): ")
        if confirm != 'SIM':
            print("❌ Operação cancelada pelo usuário")
            return
    
    # Busca específica primeiro
    await search_specific_number()
    
    # Análise geral
    invalid_leads = await find_and_clean_invalid_leads(dry_run)
    invalid_conversations = await find_and_clean_invalid_conversations(dry_run)
    invalid_followups = await find_and_clean_invalid_followups(dry_run)
    
    # Resumo
    total_invalid = invalid_leads + invalid_conversations + invalid_followups
    
    print(f"\n" + "=" * 60)
    print(f"📊 RESUMO FINAL:")
    print(f"   Leads inválidos: {invalid_leads}")
    print(f"   Conversas inválidas: {invalid_conversations}")
    print(f"   Follow-ups inválidos: {invalid_followups}")
    print(f"   TOTAL DE ITENS INVÁLIDOS: {total_invalid}")
    
    if dry_run and total_invalid > 0:
        print(f"\n💡 Para executar a limpeza, rode:")
        print(f"   python immediate_cleanup.py --execute")
    elif not dry_run:
        print(f"\n✅ Limpeza executada com sucesso!")
        print(f"   Agora teste enviando uma mensagem nova")
    elif total_invalid == 0:
        print(f"\n🎉 Nenhum dado inválido encontrado!")
        print(f"   O problema pode estar no cache Redis ou em outra parte")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
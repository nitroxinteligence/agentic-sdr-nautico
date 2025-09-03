#!/bin/bash

# Script para iniciar o sistema completo do Náutico com Redis
echo "🚀 Iniciando Sistema SDR Náutico com Redis..."

# Parar containers existentes
echo "🔄 Parando containers existentes..."
docker-compose down

# Limpar volumes se necessário (descomente se quiser reset completo)
# docker-compose down -v

# Construir e iniciar serviços
echo "🔨 Construindo e iniciando serviços..."
docker-compose up -d --build

# Aguardar serviços subirem
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Verificar status dos serviços
echo "📊 Status dos serviços:"
docker-compose ps

# Mostrar logs iniciais
echo "📋 Logs iniciais:"
docker-compose logs --tail=20

echo ""
echo "✅ Sistema iniciado com sucesso!"
echo ""
echo "📌 PRÓXIMOS PASSOS:"
echo "   1. Execute: docker-compose logs -f sdr-ia (para acompanhar logs)"
echo "   2. Execute: docker exec -it sdr-ia-nautico python start_workers.py"
echo "      (para iniciar workers de follow-up)"
echo ""
echo "🌐 Acesso:"
echo "   - API: http://localhost:8000"
echo "   - Health: http://localhost:8000/health"
echo "   - Redis: localhost:6379"
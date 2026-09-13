#!/usr/bin/env sh
# Derruba o Langfuse local (se estiver de pé), apaga todos os dados (volumes do Postgres,
# ClickHouse e MinIO), e sobe de novo do zero, com o mesmo projeto/chaves de sempre
# (provisionados via LANGFUSE_INIT_* no .env desta pasta).
set -e

cd "$(dirname "$0")"

echo "Derrubando containers e apagando volumes..."
docker compose down -v

echo "Subindo de novo..."
docker compose up -d

echo "Aguardando o Langfuse ficar pronto..."
for i in $(seq 1 30); do
    code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/public/health 2>/dev/null || echo "000")
    if [ "$code" = "200" ]; then
        echo "Pronto (tentativa $i). UI em http://localhost:3000"
        exit 0
    fi
    sleep 10
done

echo "Não respondeu depois de 5 minutos. Rode 'docker compose logs' nesta pasta pra investigar." >&2
exit 1

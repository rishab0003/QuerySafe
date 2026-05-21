#!/usr/bin/env bash
set -euo pipefail

echo "Checking QuerySafe services..."

OK=0
FAIL=0

check() {
  name=$1
  shift
  if "$@" >/dev/null 2>&1; then
    echo "[✓] $name"
    OK=$((OK+1))
  else
    echo "[✗] $name"
    FAIL=$((FAIL+1))
  fi
}

check "Nginx (frontend)" curl -fsS http://localhost
check "Backend /api/health" curl -fsS http://localhost/api/health
check "Postgres" docker exec querysafe-postgres pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-querysafe}
check "Redis" docker exec querysafe-redis redis-cli -a ${REDIS_PASSWORD:-changeme} ping
check "Chroma" curl -fsS http://localhost:8001/api/v1/heartbeat

echo "OK: $OK  FAIL: $FAIL"
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi

#!/usr/bin/env bash
set -euo pipefail

OUT=.env
if [ -f "$OUT" ]; then
  echo ".env already exists. Won't overwrite. Copy .env.example to .env and edit as needed." >&2
  exit 1
fi

echo "Generating secrets into $OUT"
cat > $OUT <<EOF
# Generated .env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$(openssl rand -hex 24)
POSTGRES_DB=querysafe
DATABASE_URL=postgresql://postgres:$(openssl rand -hex 8)@postgres:5432/querysafe
REDIS_PASSWORD=$(openssl rand -hex 32)
REDIS_URL=redis://:$(openssl rand -hex 32)@redis:6379
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
AI_PROVIDER=openai
JWT_SECRET=$(openssl rand -hex 64)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=$(openssl rand -base64 32)
CHROMA_URL=http://chroma:8001
NEXT_PUBLIC_API_URL=http://localhost/api
APP_ENV=development
DEBUG=false
EOF

echo "Wrote $OUT -- review and add provider API keys before running the stack."

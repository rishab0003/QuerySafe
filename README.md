QuerySafe — Development & DevOps entry

Quick start

1. Generate `.env` (won't overwrite existing):

```bash
chmod +x scripts/generate_secrets.sh
./scripts/generate_secrets.sh
```

2. Review and add provider API keys to `.env`.

3. Build and start the stack:

```bash
docker compose up --build
```

4. Verify services:

```bash
chmod +x scripts/healthcheck.sh
./scripts/healthcheck.sh
```

Files added by DevOps guide implementation:

- [docker-compose.yml](docker-compose.yml)
- [nginx/nginx.conf](nginx/nginx.conf)
- [backend/Dockerfile](backend/Dockerfile)
- [frontend/Dockerfile](frontend/Dockerfile)
- [.env.example](.env.example)
- [migrations/001_init.sql](migrations/001_init.sql)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [scripts/generate_secrets.sh](scripts/generate_secrets.sh)
- [scripts/healthcheck.sh](scripts/healthcheck.sh)


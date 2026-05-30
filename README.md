QuerySafe — AI-assisted safe SQL for analytics and demos

Overview

QuerySafe is a demo application that translates natural-language queries into read-only SQL against configured databases while applying safety checks (RBAC, schema validation, and injection detection). It includes a FastAPI backend, a Next.js frontend, a Postgres demo database, and optional AI integrations for NL→SQL (Gemini / Grok / mock).

Contents

- `backend/` — FastAPI application, AI pipeline, auth, adapters for multiple DBs
- `frontend/` — Next.js UI for demos and dashboards
- `migrations/` — SQL migrations and demo dataset
- `nginx/` — reverse proxy used in docker-compose

Quickstart (Docker)

1. Create or update your `.env` (the repo includes `.env.example`):

```bash
chmod +x scripts/generate_secrets.sh
./scripts/generate_secrets.sh
# Edit .env to add provider keys (see AI section below)
```

2. Build and start the stack:

```bash
docker compose up --build -d
```

3. Verify services are running:

```bash
chmod +x scripts/healthcheck.sh
./scripts/healthcheck.sh
```

4. Open the frontend at `http://localhost:3000` and the API at `http://localhost:8000`.

AI provider / API keys

To enable live NL→SQL generation you can set provider credentials in `.env`:

- `GEMINI_API_KEY` — API key for Gemini (google-genai)
- `GEMINI_MODEL` — model id (defaults to `models/gemini-1.5-flash`)
- `GROQ_API_KEY` / `GROQ_MODEL` — if using Groq

If no provider is configured the backend will fall back to a deterministic mock mode suitable for demos.

Running tests

Backend unit tests are in `backend/tests/`. Run them from the repo root:

```bash
pytest -q
```

API usage (example)

1. Create a database connection via the API (`POST /database/connect`).
2. Authenticate as the seeded admin (see `scripts/` for bootstrap). The default seeded admin email is `admin@querysafe.io`.
3. Call `POST /ai/query` with JSON payload:

```json
{
	"user_prompt": "Show the top tickets by response count",
	"connection_id": "<your-connection-id>",
	"role": "support",
	"session_id": ""
}
```

Troubleshooting

- If model responses reference tables/columns not present in the target DB, ensure the demo schema is loaded (`migrations/`), or rely on the mock fallback by omitting `GEMINI_API_KEY`.
- For long Docker builds (AI deps), set `USE_MINIMAL_DEPS=true` in the backend build args to speed up iterations when you don't need live LLMs.

Contributing

Contributions and bug reports are welcome. Open issues or PRs with focused changes. For changes to the AI pipeline see `backend/ai/pipeline.py` and the adapter implementations in `backend/database/adapters/`.

Seeded/demo credentials

- Email: admin@querysafe.io
- Default bootstrap password (if not overridden): `QsBootstrap9!`

Files of interest

- `backend/ai/pipeline.py` — NL→SQL pipeline and LLM adapters
- `backend/auth/` — authentication and OTP/2FA helpers
- `backend/database/adapters/postgres.py` — Postgres adapter and schema enforcement

License & notes

This repository is provided for demo and development purposes. Review configuration and secrets before deploying to production.




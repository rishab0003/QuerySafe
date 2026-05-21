FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps needed for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Install into a prefix so runtime image can copy only installed packages
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="QuerySafe Backend"
LABEL org.opencontainers.image.description="AI-powered read-only NL database assistant"
LABEL org.opencontainers.image.version="1.0.0"

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system appuser && adduser --system --ingroup appuser --uid 1001 appuser

WORKDIR /app

# Copy installed packages and application code
COPY --from=builder /install /install
ENV PATH=/install/bin:$PATH PYTHONPATH=/install/lib/python3.11/site-packages:/app
COPY --chown=appuser:appuser . /app

# Attempt to pre-cache model (best effort)
RUN python -c "import importlib
try:
    importlib.import_module('sentence_transformers')
    from sentence_transformers import SentenceTransformer
    SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    pass" || true

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
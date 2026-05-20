"""
main.py — QuerySafe FastAPI application entry point.

Registers all module routers and configures:
  - CORS (adjust origins for production)
  - Global exception handlers
  - OpenAPI docs at /api/docs
  - Startup / shutdown lifecycle events
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("querysafe")


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown hooks)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("QuerySafe backend starting up…")
    # Pre-warm the embedding model so first request isn't slow
    try:
        from ai.embeddings import _get_embedding_model
        _get_embedding_model()
        logger.info("Sentence-transformer model loaded.")
    except Exception as exc:
        logger.warning(f"Could not pre-warm embedding model: {exc}")
    yield
    logger.info("QuerySafe backend shutting down.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="QuerySafe API",
    description=(
        "AI-powered, read-only natural language database assistant for enterprise teams. "
        "Converts plain-English questions into safe SQL and returns structured results."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost,http://localhost:3000,http://localhost:80",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again later."},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# AI module — Person 1
from ai.routes import router as ai_router
app.include_router(ai_router)

# Auth module — Person 2 (placeholder imports; module created by P2)
try:
    from auth.routes import router as auth_router
    app.include_router(auth_router)
except ImportError:
    logger.warning("Auth module not found — skipping auth routes (P2 module not yet integrated).")

# Database module — Person 3
try:
    from database.routes import router as db_router
    app.include_router(db_router)
except ImportError:
    logger.warning("Database module not found — skipping database routes (P3 module not yet integrated).")

# Security module — Person 2
try:
    from security.routes import router as security_router
    app.include_router(security_router)
except ImportError:
    logger.warning("Security module not found — skipping security routes (P2 module not yet integrated).")


# ---------------------------------------------------------------------------
# Root health check (used by Docker HEALTHCHECK and load balancer)
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"], summary="Global health check")
async def health():
    return {"status": "ok", "service": "querysafe-backend"}


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "QuerySafe API v1.0.0 — see /api/docs for documentation."}

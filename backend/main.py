from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from auth.routes import router as auth_router
from security.routes import router as security_router
try:
    from ai.routes import router as ai_router
except Exception:
    ai_router = None

from security.middleware import SecurityMiddleware
from auth.middleware import AuthContextMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("querysafe")


def create_app() -> FastAPI:
    app = FastAPI(title="QuerySafe API")

    # CORS
    allowed = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000").split(",")
    app.add_middleware(CORSMiddleware, allow_origins=allowed, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    # Security middleware
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(AuthContextMiddleware)

    # Include routers
    app.include_router(auth_router)
    app.include_router(security_router)
    if ai_router is not None:
        app.include_router(ai_router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()

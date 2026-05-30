from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers and middleware where available (work with minimal deps)
from auth.routes import router as auth_router
from auth.oauth_routes import router as oauth_router
from auth.admin_routes import router as admin_router
from auth.middleware import AuthContextMiddleware

try:
    from security.routes import router as security_router
    from security.middleware import SecurityMiddleware
except Exception:
    security_router = None
    SecurityMiddleware = None

try:
    from ai.routes import router as ai_router
except Exception:
    ai_router = None
try:
    from demo.routes import router as demo_router
except Exception:
    demo_router = None
try:
    from database.routes import router as database_router
except Exception:
    database_router = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("querysafe")


def create_app() -> FastAPI:
    app = FastAPI(title="QuerySafe API")

    # CORS
    # Include the frontend dev server port 3001 by default for local development
    allowed = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000,http://localhost:3001").split(",")
    app.add_middleware(CORSMiddleware, allow_origins=allowed, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    # Security middleware (only add if available)
    if SecurityMiddleware is not None:
        app.add_middleware(SecurityMiddleware)
    if AuthContextMiddleware is not None:
        app.add_middleware(AuthContextMiddleware)

    # Include routers if available
    if auth_router is not None:
        app.include_router(auth_router)
    if oauth_router is not None:
        app.include_router(oauth_router)
    if admin_router is not None:
        app.include_router(admin_router)
    if security_router is not None:
        app.include_router(security_router)
    if ai_router is not None:
        app.include_router(ai_router)
    if demo_router is not None:
        app.include_router(demo_router, prefix="/demo")
    if database_router is not None:
        app.include_router(database_router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()

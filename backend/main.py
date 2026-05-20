"""
main.py — Entry point for QuerySafe Backend.
QuerySafe — Person 2: Security & Auth
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from auth.models import create_tables
from auth.routes import router as auth_router, limiter
from security.routes import router as security_router

# 1. FastAPI app setup
app = FastAPI(
    title="QuerySafe Auth & Security API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 2. Add SlowAPI Limiter state & custom 429 error handler
app.state.limiter = limiter
@app.exception_handler(RateLimitExceeded)
def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please wait a minute before retrying."}
    )

# 3. CORSMiddleware setup
origins = [
    "http://localhost:3000",
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(security_router, prefix="/api")


# 5. Startup handler to create database tables
@app.on_event("startup")
def on_startup():
    create_tables()
    print("[QuerySafe] Server ready.")


# 6. Health check endpoint
@app.get("/api/health", tags=["System"])
def health():
    return {"status": "ok"}

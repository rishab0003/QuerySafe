from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware

from .utils import parse_bearer_token


class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.auth_token = parse_bearer_token(request.headers.get("authorization"))
        return await call_next(request)


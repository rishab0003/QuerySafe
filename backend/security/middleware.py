from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

from .audit import log_security_violation


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # simple payload size check
        try:
            size = int(request.headers.get("content-length", "0"))
        except Exception:
            size = 0
        if size > 1_000_000:
            log_security_violation(None, "OVERSIZED_PAYLOAD", "Payload too large", ip=getattr(request.client, 'host', None))
            return PlainTextResponse("Payload too large", status_code=413)
        return await call_next(request)


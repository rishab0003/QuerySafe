from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from pydantic import BaseModel

from .utils import utcnow


@dataclass
class StoredUser:
    id: str
    email: str
    hashed_password: str
    department: str
    role: str
    totp_secret: str | None = None
    is_2fa_enabled: bool = False
    refresh_token_jti: str | None = None
    refresh_token_expires_at: datetime | None = None
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def public_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "department": self.department,
            "role": self.role,
            "is_2fa_enabled": self.is_2fa_enabled,
            "created_at": self.created_at.isoformat(),
        }


class AuthenticatedUser(BaseModel):
    id: str
    email: str
    department: str
    role: str
    is_2fa_enabled: bool = False


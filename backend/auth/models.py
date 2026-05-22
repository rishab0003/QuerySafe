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
    full_name: str = ""
    totp_secret: str | None = None
    is_2fa_enabled: bool = False
    is_active: bool = False
    approval_status: str = "pending"
    approved_by: str | None = None
    approved_at: datetime | None = None
    refresh_token_jti: str | None = None
    refresh_token_expires_at: datetime | None = None
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def public_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "department": self.department,
            "role": self.role,
            "is_2fa_enabled": self.is_2fa_enabled,
            "is_active": self.is_active,
            "approval_status": self.approval_status,
            "created_at": self.created_at.isoformat(),
        }

    def can_authenticate(self) -> bool:
        return self.approval_status == "approved" and self.is_active


class AuthenticatedUser(BaseModel):
    id: str
    email: str
    full_name: str = ""
    department: str
    role: str
    is_2fa_enabled: bool = False
    approval_status: str = "approved"

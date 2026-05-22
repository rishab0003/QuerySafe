from __future__ import annotations

import re

from pydantic import BaseModel, field_validator

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ALLOWED_ROLES = {"admin", "hr", "finance", "sales", "support", "viewer"}


class RegisterRequest(BaseModel):
    email: str
    password: str
    department: str
    role: str

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.fullmatch(value.strip()):
            raise ValueError("Invalid email format.")
        return value.strip().lower()

    @field_validator("department", "role")
    @classmethod
    def _normalize_fields(cls, value: str, info) -> str:
        normalized = value.strip().lower()
        if info.field_name == "role" and normalized not in ALLOWED_ROLES:
            raise ValueError("Unsupported role.")
        return normalized


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.fullmatch(value.strip()):
            raise ValueError("Invalid email format.")
        return value.strip().lower()


class SetupTwoFactorRequest(BaseModel):
    email: str | None = None
    temp_token: str | None = None


class VerifyTwoFactorRequest(BaseModel):
    temp_token: str
    code: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    token: str


class LoginResponse(BaseModel):
    requires_2fa: bool = True
    temp_token: str
    setup_required: bool = False


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class TwoFactorSetupResponse(BaseModel):
    secret: str
    otpauth_uri: str
    qr_code_base64: str


class UserResponse(BaseModel):
    id: str
    email: str
    department: str
    role: str
    is_2fa_enabled: bool
    created_at: str


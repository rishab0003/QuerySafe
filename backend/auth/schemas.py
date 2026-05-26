from __future__ import annotations

import re

from pydantic import BaseModel, field_validator

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ALLOWED_ROLES = {"admin", "hr", "finance", "sales", "support", "viewer"}
SELF_REGISTER_ROLES = {"viewer"}
ALLOWED_DEPARTMENTS = {"engineering", "hr", "finance", "sales", "support", "general"}


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    department: str = "general"

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.fullmatch(value.strip()):
            raise ValueError("Invalid email format.")
        return value.strip().lower()

    @field_validator("department")
    @classmethod
    def _normalize_department(cls, value: str) -> str:
        normalized = value.strip().lower() or "general"
        if normalized not in ALLOWED_DEPARTMENTS:
            raise ValueError("Unsupported department.")
        return normalized

    @field_validator("full_name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        name = value.strip()
        if len(name) < 2:
            raise ValueError("Full name is required.")
        return name


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
    method: str | None = None  # 'qr' or 'email'


class VerifyTwoFactorRequest(BaseModel):
    temp_token: str
    code: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    token: str


class ApproveUserRequest(BaseModel):
    role: str
    department: str = "general"

    @field_validator("role", "department")
    @classmethod
    def _normalize(cls, value: str, info) -> str:
        normalized = value.strip().lower()
        if info.field_name == "role" and normalized not in ALLOWED_ROLES:
            raise ValueError("Unsupported role.")
        if info.field_name == "department" and normalized not in ALLOWED_DEPARTMENTS:
            raise ValueError("Unsupported department.")
        return normalized


class UpdateRoleRequest(BaseModel):
    role: str
    department: str | None = None

    @field_validator("role")
    @classmethod
    def _validate_role(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_ROLES:
            raise ValueError("Unsupported role.")
        return normalized


class CreateUserRequest(BaseModel):
    email: str
    password: str
    full_name: str
    department: str = "general"
    role: str = "viewer"

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.fullmatch(value.strip()):
            raise ValueError("Invalid email format.")
        return value.strip().lower()

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        password = value.strip()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return password

    @field_validator("full_name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        name = value.strip()
        if len(name) < 2:
            raise ValueError("Full name is required.")
        return name

    @field_validator("department")
    @classmethod
    def _normalize_department(cls, value: str) -> str:
        normalized = value.strip().lower() or "general"
        if normalized not in ALLOWED_DEPARTMENTS:
            raise ValueError("Unsupported department.")
        return normalized

    @field_validator("role")
    @classmethod
    def _normalize_role(cls, value: str) -> str:
        normalized = value.strip().lower() or "viewer"
        if normalized not in ALLOWED_ROLES:
            raise ValueError("Unsupported role.")
        return normalized


class LoginResponse(BaseModel):
    requires_2fa: bool = True
    temp_token: str | None = None
    setup_required: bool = False
    approval_pending: bool = False
    message: str | None = None


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class TwoFactorSetupResponse(BaseModel):
    secret: str | None = None
    otpauth_uri: str | None = None
    qr_code_base64: str | None = None
    otp_code: str | None = None
    smtp_configured: bool | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str = ""
    department: str
    role: str
    is_2fa_enabled: bool
    is_active: bool = False
    approval_status: str = "pending"
    created_at: str

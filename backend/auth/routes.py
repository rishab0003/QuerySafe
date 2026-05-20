"""
auth/routes.py — Authentication API routes for registration, login, 2FA, token refresh, and logout.
QuerySafe — Person 2: Security & Auth
"""

from datetime import datetime, timezone, timedelta
import re

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from auth.models import User, get_db, UserRole
from auth.jwt import (
    create_access_token, create_refresh_token, verify_token,
    blacklist_token, get_current_user
)
from auth.totp import (
    generate_totp_secret, generate_qr_code, verify_totp_code
)
from security.encryption import encrypt_text, decrypt_text
from security.audit import log_action
from jose import jwt
import os

# JWT config for 2FA temp token decoding
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-here")
ALGORITHM = "HS256"

# SlowAPI Limiter instance
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Authentication"])

import bcrypt



# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters, at least 1 uppercase and 1 number")
    role: UserRole = UserRole.support


class RegisterResponse(BaseModel):
    message: str
    email: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class LoginResponse2FA(BaseModel):
    requires_2fa: bool
    temp_token: str


class Verify2FARequest(BaseModel):
    temp_token: str
    code: str = Field(..., min_length=6, max_length=6)


class Setup2FAResponse(BaseModel):
    message: str
    qr_code: str
    manual_code: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def validate_password_strength(password: str) -> None:
    """Validate password: min 8 chars, 1 uppercase, 1 number."""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long."
        )
    if not any(char.isupper() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter."
        )
    if not any(char.isdigit() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one digit (number)."
        )


def create_temp_2fa_token(user_id: str, email: str, role: str) -> str:
    """Generate a short-lived stateful temp token for 2FA validation."""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "purpose": "2fa_pending",
        "type": "temp_2fa",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account with role-based access.
    """
    # 1. Password validation
    validate_password_strength(body.password)

    # 2. Check if email exists
    existing_user = db.query(User).filter(User.email == body.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email is already registered."
        )

    # 3. Hash and save using standard native bcrypt library
    hashed_pwd = bcrypt.hashpw(body.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(
        email=body.email,
        hashed_password=hashed_pwd,
        role=body.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. Log action
    log_action(
        db=db,
        action="register_success",
        user_id=str(new_user.id),
        user_email=new_user.email,
        user_role=new_user.role.value,
        resource="/auth/register",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True
    )

    return RegisterResponse(
        message="User registered successfully",
        email=new_user.email,
        role=new_user.role.value
    )


@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    """
    User login. Triggers 2FA challenge if 2FA is enabled.
    """
    user = db.query(User).filter(User.email == body.email).first()
    
    # Simple check for password and user validity using standard native bcrypt library
    if not user or not bcrypt.checkpw(body.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        log_action(
            db=db,
            action="login_failed",
            user_id=str(user.id) if user else None,
            user_email=body.email,
            user_role=user.role.value if user else None,
            resource="/auth/login",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    # If 2FA is enabled: return temp token
    if user.is_2fa_enabled:
        temp_token = create_temp_2fa_token(str(user.id), user.email, user.role.value)
        return LoginResponse2FA(
            requires_2fa=True,
            temp_token=temp_token
        )

    # Complete regular login if no 2FA is enabled
    user.last_login = datetime.utcnow()
    db.commit()

    # Create access and refresh tokens
    token_data = {"user_id": str(user.id), "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    log_action(
        db=db,
        action="login_success",
        user_id=str(user.id),
        user_email=user.email,
        user_role=user.role.value,
        resource="/auth/login",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role.value
    )


@router.post("/verify-2fa", response_model=TokenResponse)
def verify_2fa(request: Request, body: Verify2FARequest, db: Session = Depends(get_db)):
    """
    Submit the 6-digit TOTP code to complete login with 2FA.
    """
    try:
        payload = jwt.decode(body.temp_token, JWT_SECRET, algorithms=[ALGORITHM])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired temporary token."
        )

    if payload.get("purpose") != "2fa_pending":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token purpose."
        )

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not set up on this account."
        )

    # Decrypt stored TOTP secret
    try:
        decrypted_secret = decrypt_text(user.totp_secret)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Encryption layer error during 2FA."
        )

    # Verify code
    if not verify_totp_code(decrypted_secret, body.code):
        log_action(
            db=db,
            action="login_2fa_failed",
            user_id=str(user.id),
            user_email=user.email,
            user_role=user.role.value,
            resource="/auth/verify-2fa",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA verification code."
        )

    # Correct code: Complete login
    user.last_login = datetime.utcnow()
    db.commit()

    token_data = {"user_id": str(user.id), "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    log_action(
        db=db,
        action="login_success_2fa",
        user_id=str(user.id),
        user_email=user.email,
        user_role=user.role.value,
        resource="/auth/verify-2fa",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role.value
    )


@router.post("/setup-2fa", response_model=Setup2FAResponse)
def setup_2fa(request: Request, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Setup 2FA for the current user. Generates secret, encrypts it, and returns the QR code.
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # 1. Generate new TOTP secret
    secret = generate_totp_secret()

    # 2. Encrypt and save
    encrypted_secret = encrypt_text(secret)
    user.totp_secret = encrypted_secret
    user.is_2fa_enabled = True
    db.commit()

    # 3. Generate QR code
    qr_code_base64 = generate_qr_code(secret, user.email)

    log_action(
        db=db,
        action="setup_2fa_success",
        user_id=str(user.id),
        user_email=user.email,
        user_role=user.role.value,
        resource="/auth/setup-2fa",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True
    )

    return Setup2FAResponse(
        message="2FA Setup successful. Scan the QR code with your authenticator app.",
        qr_code=qr_code_base64,
        manual_code=secret
    )


@router.post("/refresh", response_model=RefreshResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    """
    Obtain a new access token using a valid, non-blacklisted refresh token.
    """
    try:
        payload = verify_token(body.refresh_token, "refresh")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc)
        )

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user session or user deactivated."
        )

    token_data = {"user_id": str(user.id), "email": user.email, "role": user.role.value}
    new_access_token = create_access_token(token_data)

    return RefreshResponse(
        access_token=new_access_token
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(request: Request, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Invalidate current token by blacklisting it in Redis.
    """
    raw_token = current_user.get("_raw_token")
    if raw_token:
        # Standard access token lifespan is 30 mins (1800s)
        blacklist_token(raw_token, expires_in_seconds=1800)

    log_action(
        db=db,
        action="logout",
        user_id=current_user["user_id"],
        user_email=current_user["email"],
        user_role=current_user["role"],
        resource="/auth/logout",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True
    )

    return LogoutResponse(
        message="Logged out successfully"
    )

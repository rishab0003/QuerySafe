from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError

from auth.blacklist import add_to_blacklist
from auth.jwt import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    create_temp_token,
    decode_token,
    blacklist_token,
)
from auth.password import validate_password_strength
from auth.schemas import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    SetupTwoFactorRequest,
    TokenPairResponse,
    TwoFactorSetupResponse,
    UserResponse,
    VerifyTwoFactorRequest,
)
from auth.services import (
    authenticate_user,
    get_user_by_email,
    get_user_by_id,
    mark_2fa_enabled,
    register_user,
    set_refresh_token_state,
    set_totp_secret,
    startup as auth_startup,
)
from auth.dependencies import get_current_user
from auth.totp import generate_qr_code, generate_totp_secret, verify_totp_code
from auth.email_otp import (
    generate_otp_for_user,
    is_smtp_configured,
    send_otp_via_smtp,
    verify_otp_for_user,
)
from security.audit import log_event, log_security_violation
from security.rate_limit import allow_request

router = APIRouter(prefix="/auth", tags=["Auth"])

# Initialize store (Postgres or in-memory) on import
auth_startup()


def _client_ip(request: Request | None) -> str:
    if request and request.client and request.client.host:
        return request.client.host
    return "unknown"


def _user_payload(user) -> UserResponse:
    return UserResponse(**user.public_dict())


def _issue_token_pair(user) -> TokenPairResponse:
    access_payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "department": user.department,
    }
    refresh_payload = dict(access_payload)
    access_token = create_access_token(access_payload)
    refresh_token = create_refresh_token(refresh_payload)
    refresh_claims = decode_token(refresh_token)
    set_refresh_token_state(
        user.id,
        refresh_claims["jti"],
        datetime.fromtimestamp(int(refresh_claims["exp"]), tz=UTC),
    )
    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in_seconds=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/register", response_model=UserResponse)
async def register(body: RegisterRequest, request: Request):
    allowed, reason = validate_password_strength(body.password)
    if not allowed:
        log_security_violation(None, "WEAK_PASSWORD", reason, ip=_client_ip(request))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=reason)
    if get_user_by_email(body.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
    user = register_user(
        body.email,
        body.password,
        body.department,
        "viewer",
        full_name=body.full_name,
        approval_status="pending",
        is_active=False,
    )
    log_event(user.id, "REGISTER_SUCCESS", ip=_client_ip(request), metadata={"email": user.email})
    return _user_payload(user)


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, request: Request):
    if not allow_request("login", body.email):
        log_security_violation(None, "RATE_LIMIT", "Login rate limit exceeded.", ip=_client_ip(request))
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts.")
    user = authenticate_user(body.email, body.password)
    if user is None:
        log_security_violation(None, "FAILED_LOGIN", "Invalid credentials.", ip=_client_ip(request), metadata={"email": body.email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    if user.approval_status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account was not approved. Contact your administrator.",
        )
    if not user.can_authenticate():
        return LoginResponse(
            requires_2fa=False,
            temp_token=None,
            approval_pending=True,
            message="Your account is pending admin approval.",
        )
    temp_token = create_temp_token(
        {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "department": user.department,
        }
    )
    log_event(user.id, "LOGIN_SUCCESS", ip=_client_ip(request), metadata={"requires_2fa": True})
    return LoginResponse(requires_2fa=True, temp_token=temp_token, setup_required=not bool(user.totp_secret))


@router.post("/setup-2fa", response_model=TwoFactorSetupResponse)
async def setup_2fa(body: SetupTwoFactorRequest, request: Request):
    user = None
    if body.temp_token:
        try:
            claims = decode_token(body.temp_token)
            user = get_user_by_id(claims.get("sub"))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid temp token.") from exc
    elif body.email:
        user = get_user_by_email(body.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    method = (body.method or "qr").lower()
    log_event(user.id, "2FA_SETUP_REQUEST", ip=_client_ip(request), metadata={"method": method})
    if method == "email":
        code = generate_otp_for_user(user.id, user.email)
        smtp_ok = False
        if is_smtp_configured():
            smtp_ok = send_otp_via_smtp(user.email, code)
        # If SMTP not configured or failed, return otp_code in response (dev fallback)
        return TwoFactorSetupResponse(secret=None, otpauth_uri=None, qr_code_base64=None, otp_code=(code if not smtp_ok else None), smtp_configured=smtp_ok)

    # default to QR/TOTP
    secret = user.totp_secret or generate_totp_secret()
    set_totp_secret(user.id, secret)
    qr_code_base64 = generate_qr_code(secret, user.email)
    otpauth_uri = f"otpauth://totp/QuerySafe:{user.email}?secret={secret}&issuer=QuerySafe"
    log_event(user.id, "2FA_SETUP", ip=_client_ip(request))
    return TwoFactorSetupResponse(secret=secret, otpauth_uri=otpauth_uri, qr_code_base64=qr_code_base64, smtp_configured=False)


@router.post("/verify-2fa", response_model=TokenPairResponse)
async def verify_2fa(body: VerifyTwoFactorRequest, request: Request):
    try:
        claims = decode_token(body.temp_token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid temp token.") from exc
    user = get_user_by_id(claims.get("sub"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found.")
    if not user.can_authenticate():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending admin approval.",
        )
    # If a TOTP secret exists, prefer TOTP verification
    if user.totp_secret:
        if not verify_totp_code(user.totp_secret, body.code):
            log_security_violation(user.id, "FAILED_2FA", "Invalid TOTP code.", ip=_client_ip(request))
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid verification code.")
        mark_2fa_enabled(user.id, True)
        log_event(user.id, "2FA_SUCCESS", ip=_client_ip(request))
        return _issue_token_pair(user)

    # Otherwise, attempt email OTP verification
    if verify_otp_for_user(user.id, body.code):
        mark_2fa_enabled(user.id, True)
        log_event(user.id, "2FA_EMAIL_SUCCESS", ip=_client_ip(request))
        return _issue_token_pair(user)

    log_security_violation(user.id, "FAILED_2FA", "Invalid verification code.", ip=_client_ip(request))
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid verification code.")
    mark_2fa_enabled(user.id, True)
    log_event(user.id, "2FA_SUCCESS", ip=_client_ip(request))
    return _issue_token_pair(user)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(body: RefreshRequest, request: Request):
    try:
        claims = decode_token(body.refresh_token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.") from exc
    if claims.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token required.")
    user = get_user_by_id(claims.get("sub"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    if user.refresh_token_jti and claims.get("jti") != user.refresh_token_jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been rotated.")
    blacklist_token(body.refresh_token)
    log_event(user.id, "TOKEN_REFRESH", ip=_client_ip(request))
    return _issue_token_pair(user)


@router.post("/logout")
async def logout(body: LogoutRequest, request: Request):
    add_to_blacklist(body.token)
    log_event(None, "LOGOUT", ip=_client_ip(request))
    return {"detail": "Logged out successfully."}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return _user_payload(current_user)


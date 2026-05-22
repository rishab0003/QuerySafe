from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from auth.jwt import create_temp_token
from auth.oauth import (
    github_authorize_url,
    github_exchange_code,
    google_authorize_url,
    google_exchange_code,
    oauth_callback_redirect,
)
from auth.services import create_oauth_user
from security.audit import log_event

router = APIRouter(prefix="/auth/oauth", tags=["OAuth"])


def _client_ip(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _redirect_after_oauth(user, request: Request) -> RedirectResponse:
    if not user.can_authenticate():
        return RedirectResponse(
            oauth_callback_redirect("status=pending"),
            status_code=status.HTTP_302_FOUND,
        )
    temp_token = create_temp_token(
        {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "department": user.department,
        }
    )
    log_event(user.id, "OAUTH_LOGIN", ip=_client_ip(request), metadata={"provider": "oauth"})
    setup = "true" if not user.totp_secret else "false"
    return RedirectResponse(
        oauth_callback_redirect(f"temp_token={temp_token}&setup_required={setup}"),
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/google/authorize")
async def google_authorize():
    try:
        url, _ = google_authorize_url()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return RedirectResponse(url, status_code=status.HTTP_302_FOUND)


@router.get("/google/callback")
async def google_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        return RedirectResponse(oauth_callback_redirect(f"error={error}"), status_code=status.HTTP_302_FOUND)
    if not code or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing OAuth code or state.")
    try:
        profile = await google_exchange_code(code, state)
        user = create_oauth_user(
            profile["email"],
            profile["full_name"],
            profile["provider"],
            profile["provider_user_id"],
        )
    except ValueError as exc:
        return RedirectResponse(oauth_callback_redirect(f"error={exc}"), status_code=status.HTTP_302_FOUND)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"OAuth failed: {exc}") from exc
    return _redirect_after_oauth(user, request)


@router.get("/github/authorize")
async def github_authorize():
    try:
        url, _ = github_authorize_url()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return RedirectResponse(url, status_code=status.HTTP_302_FOUND)


@router.get("/github/callback")
async def github_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        return RedirectResponse(oauth_callback_redirect(f"error={error}"), status_code=status.HTTP_302_FOUND)
    if not code or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing OAuth code or state.")
    try:
        profile = await github_exchange_code(code, state)
        user = create_oauth_user(
            profile["email"],
            profile["full_name"],
            profile["provider"],
            profile["provider_user_id"],
        )
    except ValueError as exc:
        return RedirectResponse(oauth_callback_redirect(f"error={exc}"), status_code=status.HTTP_302_FOUND)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"OAuth failed: {exc}") from exc
    return _redirect_after_oauth(user, request)


@router.get("/providers")
async def oauth_providers():
    import os

    return {
        "google": bool(os.getenv("GOOGLE_CLIENT_ID")),
        "github": bool(os.getenv("GITHUB_CLIENT_ID")),
    }

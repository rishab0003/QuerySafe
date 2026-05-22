from __future__ import annotations

import os
import secrets
import time
from urllib.parse import urlencode

import httpx

# In-memory OAuth state (use Redis in production clusters)
_OAUTH_STATES: dict[str, float] = {}
_STATE_TTL_SECONDS = 600

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"


def _frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")


def _backend_public_url() -> str:
    return os.getenv("OAUTH_REDIRECT_BASE", "http://localhost:8000").rstrip("/")


def _save_state(state: str) -> None:
    now = time.time()
    expired = [k for k, v in _OAUTH_STATES.items() if now - v > _STATE_TTL_SECONDS]
    for k in expired:
        _OAUTH_STATES.pop(k, None)
    _OAUTH_STATES[state] = now


def _consume_state(state: str) -> bool:
    created = _OAUTH_STATES.pop(state, None)
    if created is None:
        return False
    return time.time() - created <= _STATE_TTL_SECONDS


def google_authorize_url() -> tuple[str, str]:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if not client_id:
        raise ValueError("GOOGLE_CLIENT_ID is not configured.")
    state = secrets.token_urlsafe(32)
    _save_state(state)
    redirect_uri = f"{_backend_public_url()}/auth/oauth/google/callback"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}", state


async def google_exchange_code(code: str, state: str) -> dict:
    if not _consume_state(state):
        raise ValueError("Invalid or expired OAuth state.")
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise ValueError("Google OAuth is not configured.")
    redirect_uri = f"{_backend_public_url()}/auth/oauth/google/callback"
    async with httpx.AsyncClient(timeout=15.0) as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        tokens = token_resp.json()
        access = tokens.get("access_token")
        if not access:
            raise ValueError("Google did not return an access token.")
        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access}"},
        )
        user_resp.raise_for_status()
        profile = user_resp.json()
    email = (profile.get("email") or "").strip().lower()
    if not email:
        raise ValueError("Google account has no email.")
    return {
        "email": email,
        "full_name": profile.get("name") or email.split("@")[0],
        "provider": "google",
        "provider_user_id": str(profile.get("id") or profile.get("sub")),
    }


def github_authorize_url() -> tuple[str, str]:
    client_id = os.getenv("GITHUB_CLIENT_ID", "").strip()
    if not client_id:
        raise ValueError("GITHUB_CLIENT_ID is not configured.")
    state = secrets.token_urlsafe(32)
    _save_state(state)
    redirect_uri = f"{_backend_public_url()}/auth/oauth/github/callback"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "read:user user:email",
        "state": state,
    }
    return f"{GITHUB_AUTH_URL}?{urlencode(params)}", state


async def github_exchange_code(code: str, state: str) -> dict:
    if not _consume_state(state):
        raise ValueError("Invalid or expired OAuth state.")
    client_id = os.getenv("GITHUB_CLIENT_ID", "").strip()
    client_secret = os.getenv("GITHUB_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise ValueError("GitHub OAuth is not configured.")
    redirect_uri = f"{_backend_public_url()}/auth/oauth/github/callback"
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        token_resp = await client.post(
            GITHUB_TOKEN_URL,
            headers=headers,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
            },
        )
        token_resp.raise_for_status()
        tokens = token_resp.json()
        access = tokens.get("access_token")
        if not access:
            raise ValueError("GitHub did not return an access token.")
        auth_header = {"Authorization": f"Bearer {access}", "Accept": "application/json"}
        user_resp = await client.get(GITHUB_USER_URL, headers=auth_header)
        user_resp.raise_for_status()
        profile = user_resp.json()
        email = (profile.get("email") or "").strip().lower()
        if not email:
            emails_resp = await client.get(GITHUB_EMAILS_URL, headers=auth_header)
            emails_resp.raise_for_status()
            for entry in emails_resp.json():
                if entry.get("primary") and entry.get("verified"):
                    email = entry.get("email", "").strip().lower()
                    break
    if not email:
        raise ValueError("GitHub account has no verified email.")
    return {
        "email": email,
        "full_name": profile.get("name") or profile.get("login") or email.split("@")[0],
        "provider": "github",
        "provider_user_id": str(profile.get("id")),
    }


def oauth_callback_redirect(query: str) -> str:
    return f"{_frontend_url()}/auth/oauth/callback?{query}"

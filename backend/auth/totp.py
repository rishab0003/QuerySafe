from __future__ import annotations

import base64
import io
import os

import pyotp
import qrcode


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def generate_otpauth_uri(secret: str, account_name: str, issuer: str | None = None) -> str:
    return pyotp.TOTP(secret).provisioning_uri(
        name=account_name,
        issuer_name=issuer or os.getenv("TOTP_ISSUER", "QuerySafe"),
    )


def generate_qr_code(secret: str, account_name: str, issuer: str | None = None) -> str:
    uri = generate_otpauth_uri(secret, account_name, issuer=issuer)
    image = qrcode.make(uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def verify_totp_code(secret: str, code: str, valid_window: int = 1) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=valid_window)


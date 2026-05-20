"""
auth/totp.py — TOTP secret generation, QR-code creation, and code verification.
QuerySafe — Person 2: Security & Auth
"""

import base64
import io

import pyotp
import qrcode


APP_NAME = "QuerySafe"


def generate_totp_secret() -> str:
    """Return a cryptographically-random Base32 TOTP secret."""
    return pyotp.random_base32()


def generate_qr_code(secret: str, email: str) -> str:
    """
    Build an otpauth:// URI and render it as a QR-code PNG.

    Returns:
        A data-URI string: "data:image/png;base64,..." ready for an <img> tag.
    """
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name=APP_NAME)

    img = qrcode.make(uri)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def verify_totp_code(secret: str, code: str) -> bool:
    """
    Verify a 6-digit TOTP code against the given secret.

    valid_window=1 accepts one 30-second window before/after the current window,
    allowing for minor clock drift between client and server.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)

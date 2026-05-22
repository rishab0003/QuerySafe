from __future__ import annotations

import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key() -> bytes:
    key_b64 = os.getenv("ENCRYPTION_KEY")
    if not key_b64:
        # For development: generate and cache an in-memory key so
        # encrypt/decrypt calls in the same process use the same key.
        global _DEV_KEY
        try:
            _DEV_KEY
        except NameError:
            _DEV_KEY = AESGCM.generate_key(bit_length=256)
        return _DEV_KEY
    return base64.b64decode(key_b64)


def encrypt_data(plaintext: bytes) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)
    return base64.b64encode(nonce + ct).decode('ascii')


def decrypt_data(token: str) -> bytes:
    key = _get_key()
    data = base64.b64decode(token)
    nonce = data[:12]
    ct = data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None)


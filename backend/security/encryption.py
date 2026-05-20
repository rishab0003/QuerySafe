"""
security/encryption.py — AES-256 encryption using cryptography.fernet.Fernet.
QuerySafe — Person 2: Security & Auth
"""

import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY environment variable is not set. Please set it in your .env file.")

try:
    # Ensure the key is valid Fernet (32 url-safe base64-encoded bytes)
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    raise RuntimeError(f"Invalid ENCRYPTION_KEY configuration: {e}")


def encrypt_text(plaintext: str) -> str:
    """
    Encrypts string, returns encrypted string starting with 'gAAAAA...'
    """
    if not plaintext:
        return ""
    encrypted_bytes = cipher_suite.encrypt(plaintext.encode())
    return encrypted_bytes.decode()


def decrypt_text(ciphertext: str) -> str:
    """
    Decrypts ciphertext back to original plaintext.
    Raises ValueError if key is wrong or data is corrupt/invalid.
    """
    if not ciphertext:
        return ""
    try:
        decrypted_bytes = cipher_suite.decrypt(ciphertext.encode())
        return decrypted_bytes.decode()
    except InvalidToken as exc:
        raise ValueError("Decryption failed. Invalid token, wrong key, or corrupt data.") from exc


def encrypt_dict(data: dict) -> dict:
    """
    Encrypts every value in a dictionary. Used for DB credentials.
    """
    encrypted_data = {}
    for k, v in data.items():
        if isinstance(v, str):
            encrypted_data[k] = encrypt_text(v)
        elif isinstance(v, (int, float, bool)):
            encrypted_data[k] = encrypt_text(str(v))
        else:
            encrypted_data[k] = v
    return encrypted_data


def decrypt_dict(data: dict) -> dict:
    """
    Reverses encrypt_dict. Decrypts every string value.
    """
    decrypted_data = {}
    for k, v in data.items():
        if isinstance(v, str) and v.startswith("gAAAAA"):
            decrypted_data[k] = decrypt_text(v)
        else:
            decrypted_data[k] = v
    return decrypted_data

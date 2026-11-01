"""Хешування паролів і JWT (без залежності від FastAPI — легко тестується окремо)."""
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from tourist_routes.api import config

_SCRYPT = {"n": 2**14, "r": 8, "p": 1}


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, **_SCRYPT)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, digest_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, **_SCRYPT)
    return hmac.compare_digest(digest.hex(), digest_hex)


def create_access_token(username: str, expires_minutes: Optional[int] = None) -> str:
    minutes = config.ACCESS_TOKEN_EXPIRE_MINUTES if expires_minutes is None else expires_minutes
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """Повертає ім'я користувача або None, якщо токен недійсний чи прострочений."""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return None
    username = payload.get("sub")
    return username if isinstance(username, str) else None

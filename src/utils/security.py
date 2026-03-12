"""Утилиты безопасности: хеширование паролей и JWT-токены."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime, timedelta, timezone

AUTH_SECRET_ENV = "AUTH_SECRET_KEY"
DEFAULT_ACCESS_TOKEN_TTL_MINUTES = 60


def _b64url_encode(raw: bytes) -> str:
    """Кодирует байты в URL-safe base64 без символов заполнения."""

    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(raw: str) -> bytes:
    """Декодирует URL-safe base64 строку."""

    padding = "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode((raw + padding).encode("ascii"))


def _get_secret_key() -> str:
    """Возвращает секрет для подписи токенов из окружения."""

    return os.getenv(AUTH_SECRET_ENV, "dev-secret-change-me")


def hash_password(password: str) -> str:
    """Хеширует пароль алгоритмом PBKDF2-HMAC-SHA256."""

    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120_000)
    return f"pbkdf2_sha256${salt}${derived.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль относительно сохраненного хеша."""

    try:
        method, salt, expected = password_hash.split("$", 2)
    except ValueError:
        return False

    if method != "pbkdf2_sha256":
        return False

    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120_000)
    return hmac.compare_digest(derived.hex(), expected)


def create_access_token(*, user_id: int, email: str, expires_minutes: int = DEFAULT_ACCESS_TOKEN_TTL_MINUTES) -> str:
    """Создает JWT access token с подписью HS256."""

    header = {"alg": "HS256", "typ": "JWT"}
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }

    header_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_part}.{payload_part}".encode("ascii")
    signature = hmac.new(_get_secret_key().encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_part = _b64url_encode(signature)

    return f"{header_part}.{payload_part}.{signature_part}"


def decode_access_token(token: str) -> dict[str, object]:
    """Проверяет подпись и срок действия JWT, возвращает payload."""

    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Некорректный формат токена")

    header_part, payload_part, signature_part = parts
    signing_input = f"{header_part}.{payload_part}".encode("ascii")

    expected_signature = hmac.new(
        _get_secret_key().encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    actual_signature = _b64url_decode(signature_part)
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise ValueError("Некорректная подпись токена")

    payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
    exp_value = int(payload.get("exp", 0))
    if exp_value <= int(time.time()):
        raise ValueError("Срок действия токена истек")

    return payload

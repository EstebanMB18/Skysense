"""Redis central para OTP, refresh tokens y controles temporales.

En modo local puede usar memoria si Redis no está disponible. En ENV=production o
REDIS_REQUIRED=true la aplicación falla si Redis no responde, evitando una falsa
sensación de seguridad/persistencia.
"""
from __future__ import annotations

import time
from threading import Lock

try:
    import redis
except ImportError:  # permite pruebas locales sin Redis; Docker sí instala la dependencia
    redis = None

from app.core.config import settings

_client = None
_memory: dict[str, tuple[str, float | None]] = {}
_lock = Lock()


def _redis():
    global _client
    if _client is not None:
        return _client
    if redis is None:
        if settings.REDIS_REQUIRED or settings.ENV.lower() == "production":
            raise RuntimeError("Redis package is required but unavailable")
        return None
    try:
        client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=2)
        client.ping()
        _client = client
        return client
    except Exception:
        if settings.REDIS_REQUIRED or settings.ENV.lower() == "production":
            raise RuntimeError("Redis is required but unavailable")
        return None


def ping() -> bool:
    try:
        r = _redis()
        return bool(r.ping()) if r else True
    except Exception:
        return False


def set_value(key: str, value: str, ttl_seconds: int | None = None) -> None:
    r = _redis()
    if r:
        r.set(key, value, ex=ttl_seconds)
        return
    expires = time.time() + ttl_seconds if ttl_seconds else None
    with _lock:
        _memory[key] = (value, expires)


def get_value(key: str) -> str | None:
    r = _redis()
    if r:
        return r.get(key)
    with _lock:
        item = _memory.get(key)
        if not item:
            return None
        value, expires = item
        if expires and expires <= time.time():
            _memory.pop(key, None)
            return None
        return value


def delete(key: str) -> None:
    r = _redis()
    if r:
        r.delete(key)
        return
    with _lock:
        _memory.pop(key, None)


def incr(key: str, ttl_seconds: int) -> int:
    r = _redis()
    if r:
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl_seconds, nx=True)
        value, _ = pipe.execute()
        return int(value)
    current = int(get_value(key) or "0") + 1
    set_value(key, str(current), ttl_seconds)
    return current

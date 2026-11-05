from app.core.config import settings
from app.services.redis_store import delete, get_value, set_value


def remember_refresh(jti: str, user_id: int) -> None:
    set_value(f"refresh:{jti}", str(user_id), settings.REFRESH_TOKEN_DAYS * 86400)


def refresh_is_active(jti: str, user_id: int) -> bool:
    return get_value(f"refresh:{jti}") == str(user_id)


def revoke_refresh(jti: str) -> None:
    delete(f"refresh:{jti}")

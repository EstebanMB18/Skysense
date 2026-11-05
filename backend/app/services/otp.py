import json
import hmac

from app.core.config import settings
from app.core.security import hash_otp
from app.services.redis_store import delete, get_value, set_value


def _otp_key(email: str) -> str:
    return f"otp:{email.lower()}"


def _cooldown_key(email: str) -> str:
    return f"otp:cooldown:{email.lower()}"


def save_otp(email: str, code: str) -> tuple[bool, str]:
    email = email.lower()
    if get_value(_cooldown_key(email)):
        return False, "OTP_COOLDOWN"
    payload = {"hash": hash_otp(code), "attempts": 0}
    set_value(_otp_key(email), json.dumps(payload), settings.OTP_TTL_SECONDS)
    set_value(_cooldown_key(email), "1", settings.OTP_COOLDOWN_SECONDS)
    return True, "OK"


def verify_otp(email: str, code: str) -> tuple[bool, str]:
    key = _otp_key(email)
    raw = get_value(key)
    if not raw:
        return False, "OTP_NOT_FOUND_OR_EXPIRED"
    payload = json.loads(raw)
    attempts = int(payload.get("attempts", 0))
    if attempts >= settings.OTP_MAX_ATTEMPTS:
        delete(key)
        return False, "OTP_LOCKED"
    payload["attempts"] = attempts + 1
    set_value(key, json.dumps(payload), settings.OTP_TTL_SECONDS)
    if not hmac.compare_digest(payload["hash"], hash_otp(code)):
        return False, "OTP_INVALID"
    delete(key)
    return True, "OK"

import hmac
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.base import get_db
from app.models.entities import User

bearer = HTTPBearer(auto_error=False)


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(401, "Missing token")
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, user_id)
    if not user or user.status != "ACTIVE":
        raise HTTPException(401, "User inactive or not found")
    return user


def require_roles(*roles):
    def dep(user=Depends(current_user)):
        if user.role.name not in roles:
            raise HTTPException(403, "Forbidden")
        return user
    return dep


def require_ingest_key(x_ingest_key: str | None = Header(default=None, alias="X-Ingest-Key")):
    if not x_ingest_key or not hmac.compare_digest(x_ingest_key, settings.INGEST_API_KEY):
        raise HTTPException(401, "Invalid ingest key")
    return True

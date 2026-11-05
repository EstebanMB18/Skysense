from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_ingest_key, require_roles
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp,
    verify_password,
)
from app.db.base import get_db
from app.models.entities import Alert, Audit, Event, Health, Station, Telemetry, User
from app.schemas.api import EventIn, HealthIn, LoginRequest, OTPRequest, OTPVerify, TelemetryIn, TokenResponse
from app.services.alerts import evaluate_rules
from app.services.email import send_otp
from app.services.otp import save_otp, verify_otp
from app.services.redis_store import ping as redis_ping
from app.services.tokens import refresh_is_active, remember_refresh, revoke_refresh

router = APIRouter()
REFRESH_COOKIE = "skysense_refresh"


def audit(db, user_id, action, resource, result, ip=None):
    db.add(Audit(user_id=user_id, action=action, resource=resource, result=result, ip=ip))
    db.commit()


def client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def set_refresh_cookie(response: Response, user: User) -> str:
    refresh, jti = create_refresh_token(user.id, user.role.name)
    remember_refresh(jti, user.id)
    response.set_cookie(
        REFRESH_COOKIE,
        refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_DAYS * 86400,
        path="/api/v1/auth",
    )
    return refresh


def token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id, user.role.name),
        expires_in=settings.ACCESS_TOKEN_MINUTES * 60,
    )


@router.get("/system/health")
def system_health(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    redis_ok = redis_ping()
    status = "ok" if db_ok and redis_ok else "degraded"
    return {
        "status": status,
        "service": "skysense-api",
        "database": "ok" if db_ok else "error",
        "redis": "ok" if redis_ok else "error",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, response: Response, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or user.status != "ACTIVE" or not verify_password(data.password, user.password_hash):
        if user:
            audit(db, user.id, "LOGIN", "auth", "DENIED", client_ip(request))
        raise HTTPException(401, "Invalid credentials")
    user.last_access = datetime.now(timezone.utc)
    db.commit()
    set_refresh_cookie(response, user)
    audit(db, user.id, "LOGIN", "auth", "SUCCESS", client_ip(request))
    return token_response(user)


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh_session(
    response: Response,
    refresh_cookie: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    db: Session = Depends(get_db),
):
    if not refresh_cookie:
        raise HTTPException(401, "Missing refresh token")
    try:
        payload = decode_token(refresh_cookie, expected_type="refresh")
        user_id = int(payload["sub"])
        jti = payload["jti"]
    except Exception:
        raise HTTPException(401, "Invalid refresh token")
    if not refresh_is_active(jti, user_id):
        raise HTTPException(401, "Refresh token revoked")
    user = db.get(User, user_id)
    if not user or user.status != "ACTIVE":
        raise HTTPException(401, "User inactive or not found")
    # Refresh token rotation: revoke current and issue a new cookie.
    revoke_refresh(jti)
    set_refresh_cookie(response, user)
    return token_response(user)


@router.post("/auth/logout")
def logout(
    response: Response,
    refresh_cookie: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    if refresh_cookie:
        try:
            payload = decode_token(refresh_cookie, expected_type="refresh")
            revoke_refresh(payload["jti"])
        except Exception:
            pass
    response.delete_cookie(REFRESH_COOKIE, path="/api/v1/auth")
    audit(db, user.id, "LOGOUT", "auth", "SUCCESS")
    return {"status": "ok"}


@router.get("/auth/me")
def auth_me(user=Depends(current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.name,
        "role_description": user.role.description,
        "status": user.status,
        "last_access": user.last_access,
    }


@router.get("/users")
def list_users(user=Depends(require_roles("ADMIN")), db: Session = Depends(get_db)):
    rows = db.query(User).order_by(User.email.asc()).all()
    return [
        {"id": x.id, "email": x.email, "role": x.role.name, "status": x.status, "last_access": x.last_access}
        for x in rows
    ]


@router.post("/auth/otp/request")
def otp_request(data: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or user.status != "ACTIVE":
        # No revelar si el correo existe en despliegues públicos.
        return {"message": "If the account is eligible, an OTP was generated."}
    code = generate_otp()
    ok, reason = save_otp(data.email, code)
    if not ok:
        raise HTTPException(429, reason)
    send_otp(data.email, code)
    body = {"message": "OTP generated", "ttl_seconds": settings.OTP_TTL_SECONDS}
    if settings.ENV.lower() in {"local", "test", "development"} and settings.OTP_DELIVERY_MODE == "console":
        body["demo_code"] = code
    return body


@router.post("/auth/otp/verify", response_model=TokenResponse)
def otp_verify(data: OTPVerify, response: Response, db: Session = Depends(get_db)):
    ok, reason = verify_otp(data.email, data.code)
    if not ok:
        raise HTTPException(400, reason)
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or user.status != "ACTIVE":
        raise HTTPException(401, "User unavailable")
    set_refresh_cookie(response, user)
    return token_response(user)


@router.get("/stations")
def stations(user=Depends(current_user), db: Session = Depends(get_db)):
    return [
        {
            "id": s.id,
            "station_code": s.station_code,
            "name": s.name,
            "status": s.status,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "firmware": s.firmware,
        }
        for s in db.query(Station).all()
    ]


@router.get("/stations/{station_code}/latest")
def latest(station_code: str, user=Depends(current_user), db: Session = Depends(get_db)):
    s = db.query(Station).filter_by(station_code=station_code).first()
    if not s:
        raise HTTPException(404, "Station not found")
    t = db.query(Telemetry).filter_by(station_id=s.id).order_by(Telemetry.timestamp_utc.desc()).first()
    if not t:
        raise HTTPException(404, "No telemetry")
    ts = t.timestamp_utc.replace(tzinfo=t.timestamp_utc.tzinfo or timezone.utc)
    age = max(0, (datetime.now(timezone.utc) - ts).total_seconds())
    return {
        "station_id": s.station_code,
        "timestamp_utc": t.timestamp_utc,
        "age_seconds": round(age, 1),
        "quality": t.quality_flag,
        "temperature_c": t.temperature,
        "humidity_pct": t.humidity,
        "pressure_hpa": t.pressure,
        "wind_speed_ms": t.wind_speed,
        "wind_direction_deg": t.wind_direction,
        "density_altitude_ft": t.density_altitude,
    }


@router.get("/stations/{station_code}/history")
def history(station_code: str, limit: int = 100, user=Depends(current_user), db: Session = Depends(get_db)):
    s = db.query(Station).filter_by(station_code=station_code).first()
    if not s:
        raise HTTPException(404, "Station not found")
    rows = (
        db.query(Telemetry)
        .filter_by(station_id=s.id)
        .order_by(Telemetry.timestamp_utc.desc())
        .limit(min(max(limit, 1), 1000))
        .all()
    )
    return [
        {
            "timestamp_utc": x.timestamp_utc,
            "temperature_c": x.temperature,
            "humidity_pct": x.humidity,
            "pressure_hpa": x.pressure,
            "wind_speed_ms": x.wind_speed,
            "wind_direction_deg": x.wind_direction,
            "density_altitude_ft": x.density_altitude,
            "quality": x.quality_flag,
        }
        for x in rows
    ]


@router.get("/stations/{station_code}/health")
def station_health(station_code: str, user=Depends(current_user), db: Session = Depends(get_db)):
    s = db.query(Station).filter_by(station_code=station_code).first()
    if not s:
        raise HTTPException(404, "Station not found")
    h = db.query(Health).filter_by(station_id=s.id).order_by(Health.timestamp_utc.desc()).first()
    return None if not h else {
        "timestamp_utc": h.timestamp_utc,
        "battery_pct": h.battery,
        "rssi_dbm": h.rssi,
        "uptime_s": h.uptime,
        "memory_pct": h.memory,
        "reboots": h.reboots,
        "firmware": h.firmware,
    }


@router.get("/alerts")
def alerts(user=Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Alert).order_by(Alert.started_at.desc()).limit(100).all()
    return [
        {
            "id": a.id,
            "station": a.station.station_code,
            "rule": a.rule.name,
            "severity": a.rule.severity,
            "status": a.status,
            "value": a.trigger_value,
            "started_at": a.started_at,
        }
        for a in rows
    ]


@router.patch("/alerts/{alert_id}")
def close_alert(
    alert_id: int,
    request: Request,
    user=Depends(require_roles("ADMIN", "OPERATOR")),
    db: Session = Depends(get_db),
):
    a = db.get(Alert, alert_id)
    if not a:
        raise HTTPException(404, "Alert not found")
    a.status = "CLOSED"
    a.ended_at = datetime.now(timezone.utc)
    db.commit()
    audit(db, user.id, "CLOSE_ALERT", f"alert:{alert_id}", "SUCCESS", client_ip(request))
    return {"status": "closed"}


@router.post("/ingest/telemetry")
def ingest_telemetry(data: TelemetryIn, _=Depends(require_ingest_key), db: Session = Depends(get_db)):
    s = db.query(Station).filter_by(station_code=data.station_id).first()
    if not s:
        raise HTTPException(404, "Unknown station")
    t = Telemetry(
        station_id=s.id,
        message_id=data.message_id,
        timestamp_utc=data.timestamp_utc,
        temperature=data.temperature_c,
        humidity=data.humidity_pct,
        pressure=data.pressure_hpa,
        wind_speed=data.wind_speed_ms,
        wind_direction=data.wind_direction_deg,
        density_altitude=data.density_altitude_ft,
        quality_flag=data.quality_flag,
    )
    db.add(t)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return {"status": "duplicate"}
    evaluate_rules(
        db,
        s.id,
        {
            "temperature": data.temperature_c,
            "humidity": data.humidity_pct,
            "pressure": data.pressure_hpa,
            "wind_speed": data.wind_speed_ms,
            "wind_direction": data.wind_direction_deg,
            "density_altitude": data.density_altitude_ft,
        },
    )
    db.commit()
    return {"status": "accepted", "station": s.station_code}


@router.post("/ingest/health")
def ingest_health(data: HealthIn, _=Depends(require_ingest_key), db: Session = Depends(get_db)):
    s = db.query(Station).filter_by(station_code=data.station_id).first()
    if not s:
        raise HTTPException(404, "Station not found")
    db.add(
        Health(
            station_id=s.id,
            timestamp_utc=data.timestamp_utc,
            battery=data.battery_pct,
            rssi=data.rssi_dbm,
            uptime=data.uptime_s,
            memory=data.memory_pct,
            reboots=data.reboots,
            firmware=data.firmware,
        )
    )
    db.commit()
    return {"status": "accepted"}


@router.post("/ingest/events")
def ingest_event(data: EventIn, _=Depends(require_ingest_key), db: Session = Depends(get_db)):
    s = db.query(Station).filter_by(station_code=data.station_id).first()
    if not s:
        raise HTTPException(404, "Station not found")
    db.add(Event(station_id=s.id, timestamp_utc=data.timestamp_utc, type=data.type, severity=data.severity, detail=data.detail))
    db.commit()
    return {"status": "accepted"}

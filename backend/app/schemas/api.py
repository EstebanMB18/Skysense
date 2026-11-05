from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TelemetryIn(BaseModel):
    schema_version: str = "1.0"
    message_id: str = Field(min_length=1, max_length=100)
    station_id: str = Field(min_length=1, max_length=50)
    timestamp_utc: datetime
    temperature_c: float | None = None
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    pressure_hpa: float | None = Field(default=None, ge=300, le=1200)
    wind_speed_ms: float | None = Field(default=None, ge=0, le=150)
    wind_direction_deg: float | None = Field(default=None, ge=0, lt=360)
    density_altitude_ft: float | None = None
    quality_flag: str = Field(default="VALID", pattern=r"^(VALID|SUSPECT|INVALID|MISSING)$")


class HealthIn(BaseModel):
    station_id: str
    timestamp_utc: datetime
    battery_pct: float | None = Field(default=None, ge=0, le=100)
    rssi_dbm: float | None = None
    uptime_s: int | None = Field(default=None, ge=0)
    memory_pct: float | None = Field(default=None, ge=0, le=100)
    reboots: int | None = Field(default=None, ge=0)
    firmware: str | None = None


class EventIn(BaseModel):
    station_id: str
    timestamp_utc: datetime
    type: str = Field(min_length=1, max_length=50)
    severity: str = Field(default="INFO", pattern=r"^(INFO|WARNING|CRITICAL)$")
    detail: str | None = None

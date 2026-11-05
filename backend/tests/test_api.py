import os
from pathlib import Path

TEST_DB = Path("./test_skysense.db")
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_skysense.db"
os.environ["JWT_SECRET"] = "test-secret-long-enough-for-tests-only-123456789"
os.environ["INGEST_API_KEY"] = "test-ingest-key-12345678901234567890"
os.environ["REDIS_REQUIRED"] = "false"
os.environ["OTP_COOLDOWN_SECONDS"] = "0"

from fastapi.testclient import TestClient
from app.main import app

INGEST = {"X-Ingest-Key": os.environ["INGEST_API_KEY"]}


def auth_headers(client: TestClient):
    r = client.post("/api/v1/auth/login", json={"email": "admin@skysense.co", "password": "Admin123!"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_security_and_data_flow():
    with TestClient(app) as client:
        health = client.get("/api/v1/system/health")
        assert health.status_code == 200
        assert health.json()["database"] == "ok"

        h = auth_headers(client)
        me = client.get("/api/v1/auth/me", headers=h)
        assert me.status_code == 200 and me.json()["role"] == "ADMIN"

        # Ingesta sin clave debe rechazarse.
        payload = {
            "message_id": "test-001",
            "station_id": "SKY-001",
            "timestamp_utc": "2026-11-04T12:00:00Z",
            "temperature_c": 22.4,
            "humidity_pct": 56,
            "pressure_hpa": 1016.2,
            "wind_speed_ms": 13.1,
            "wind_direction_deg": 270,
            "density_altitude_ft": 1240,
            "quality_flag": "VALID",
        }
        assert client.post("/api/v1/ingest/telemetry", json=payload).status_code == 401
        assert client.post("/api/v1/ingest/telemetry", json=payload, headers=INGEST).status_code == 200

        latest = client.get("/api/v1/stations/SKY-001/latest", headers=h)
        assert latest.status_code == 200
        assert latest.json()["temperature_c"] == 22.4

        alerts = client.get("/api/v1/alerts", headers=h).json()
        assert any(a["rule"] == "Viento fuerte" for a in alerts)

        # El refresh token queda en cookie HttpOnly y rota.
        refreshed = client.post("/api/v1/auth/refresh")
        assert refreshed.status_code == 200
        assert "access_token" in refreshed.json()

        h2 = {"Authorization": f"Bearer {refreshed.json()['access_token']}"}
        users = client.get("/api/v1/users", headers=h2)
        assert users.status_code == 200

        # OTP en almacén temporal (Redis en producción, fallback en test).
        otp = client.post("/api/v1/auth/otp/request", json={"email": "admin@skysense.co"})
        assert otp.status_code == 200
        code = otp.json()["demo_code"]
        verified = client.post("/api/v1/auth/otp/verify", json={"email": "admin@skysense.co", "code": code})
        assert verified.status_code == 200

        logout = client.post("/api/v1/auth/logout", headers=h2)
        assert logout.status_code == 200

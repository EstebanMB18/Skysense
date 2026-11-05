import os
import uuid
from datetime import datetime, timezone
import requests

API = os.getenv("API_BASE", "http://localhost:8080/api/v1")
KEY = os.getenv("INGEST_API_KEY")
if not KEY:
    raise SystemExit("Set INGEST_API_KEY before running this script")

payload = {
    "schema_version": "1.0",
    "message_id": str(uuid.uuid4()),
    "station_id": "SKY-001",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "temperature_c": 24.6,
    "humidity_pct": 66,
    "pressure_hpa": 1011.8,
    "wind_speed_ms": 12.5,
    "wind_direction_deg": 280,
    "density_altitude_ft": 1900,
    "quality_flag": "VALID",
}
r = requests.post(f"{API}/ingest/telemetry", json=payload, headers={"X-Ingest-Key": KEY}, timeout=10)
print(r.status_code, r.text)

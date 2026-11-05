import json
import os
import sys
from datetime import datetime, timezone
import paho.mqtt.publish as publish

host = os.getenv("MQTT_HOST", "localhost")
port = int(os.getenv("MQTT_PORT", "1883"))
user = os.getenv("MQTT_USERNAME", "skynode")
password = os.getenv("MQTT_PASSWORD")
station = os.getenv("STATION_ID", "SKY-001")
if not password:
    raise SystemExit("Set MQTT_PASSWORD before publishing")

payload = {
    "schema_version": "1.0",
    "message_id": f"cli-{int(datetime.now(timezone.utc).timestamp())}",
    "station_id": station,
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "temperature_c": 24.6,
    "humidity_pct": 66,
    "pressure_hpa": 1011.8,
    "wind_speed_ms": float(sys.argv[1]) if len(sys.argv) > 1 else 8.5,
    "wind_direction_deg": 280,
    "density_altitude_ft": 1900,
    "quality_flag": "VALID",
}
publish.single(
    f"skysense/{station}/telemetry",
    json.dumps(payload),
    hostname=host,
    port=port,
    qos=1,
    auth={"username": user, "password": password},
)
print(json.dumps(payload, indent=2))

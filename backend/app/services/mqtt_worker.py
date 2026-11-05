"""Worker MQTT -> API interna.

El broker autentica al cliente MQTT y el worker usa X-Ingest-Key para acceder a
los endpoints internos de ingesta. El navegador nunca necesita esta clave.
"""
import json
import os
import time

import paho.mqtt.client as mqtt
import requests

HOST = os.getenv("MQTT_HOST", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", "1883"))
ROOT = os.getenv("MQTT_TOPIC_ROOT", "skysense")
USERNAME = os.getenv("MQTT_USERNAME", "skynode")
PASSWORD = os.getenv("MQTT_PASSWORD", "")
API = os.getenv("API_BASE", "http://backend:8000/api/v1")
INGEST_KEY = os.getenv("INGEST_API_KEY", "")


def on_connect(client, userdata, flags, reason_code, properties=None):
    print("mqtt connected", reason_code)
    client.subscribe(f"{ROOT}/+/telemetry", qos=1)
    client.subscribe(f"{ROOT}/+/health", qos=1)
    client.subscribe(f"{ROOT}/+/events", qos=1)


def on_message(client, userdata, msg):
    kind = msg.topic.split("/")[-1]
    if kind not in {"telemetry", "health", "events"}:
        return
    try:
        payload = json.loads(msg.payload.decode())
        r = requests.post(
            f"{API}/ingest/{kind}",
            json=payload,
            headers={"X-Ingest-Key": INGEST_KEY},
            timeout=10,
        )
        print(msg.topic, r.status_code, r.text)
    except Exception as exc:
        print("mqtt-worker error", exc)


if __name__ == "__main__":
    if not PASSWORD or not INGEST_KEY:
        raise RuntimeError("MQTT_PASSWORD and INGEST_API_KEY are required")
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="skysense-ingestion-worker")
    c.username_pw_set(USERNAME, PASSWORD)
    c.on_connect = on_connect
    c.on_message = on_message
    while True:
        try:
            c.connect(HOST, PORT, 60)
            c.loop_forever()
        except Exception as exc:
            print("mqtt connection error", exc, "retrying in 5s")
            time.sleep(5)

import secrets
print("JWT_SECRET=" + secrets.token_urlsafe(64))
print("INGEST_API_KEY=" + secrets.token_urlsafe(48))
print("POSTGRES_PASSWORD=" + secrets.token_urlsafe(32))
print("MQTT_PASSWORD=" + secrets.token_urlsafe(32))

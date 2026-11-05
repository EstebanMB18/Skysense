# SkySense v3.1 - Startup patch

Fixes two startup issues found on Windows/Docker Desktop:

1. Backend production validation now receives MQTT_USERNAME and MQTT_PASSWORD.
2. Mosquitto password file is explicitly owned by the `mosquitto` user before broker startup.
3. Mosquitto healthcheck no longer depends on `mosquitto_pub` being present in the runtime image.

## Apply from a clean project directory

```powershell
docker compose down
# Keep volumes if you want to preserve PostgreSQL/Redis data.
docker compose up --build -d
docker compose ps
```

If an earlier failed Mosquitto volume has stale permissions, reset only its volume:

```powershell
docker compose down
$vol = docker volume ls --format "{{.Name}}" | Select-String "mosquittodata" | ForEach-Object { $_.Line }
if ($vol) { docker volume rm $vol }
docker compose up --build -d
```

For diagnosis:

```powershell
docker compose logs --tail=100 backend
docker compose logs --tail=100 mosquitto
```

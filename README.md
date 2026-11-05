# SkySense v3 - versión cerrada para despliegue

Implementación de la plataforma SkySense conforme a la arquitectura documentada: React, FastAPI, PostgreSQL, Redis, MQTT/Mosquitto, worker de ingesta, JWT/RBAC, OTP, alertas, históricos, health y Leaflet/OpenStreetMap.

## Opción recomendada: Docker Compose

### 1. Crear secretos

En PowerShell desde la raíz:

```powershell
python .\scripts\generate_secrets.py
Copy-Item .env.example .env
notepad .env
```

Reemplaza en `.env` los valores `CHANGE_ME...` con los valores generados.

Para la demostración local deja:

```env
COOKIE_SECURE=false
OTP_DELIVERY_MODE=console
SEED_DEMO_USERS=true
CORS_ORIGINS=http://localhost:8080
```

### 2. Levantar

```powershell
docker compose up --build -d
```

### 3. Revisar estado

```powershell
docker compose ps
docker compose logs -f backend
docker compose logs -f mqtt-worker
```

Abre:

- Frontend: `http://localhost:8080`
- API vía proxy: `http://localhost:8080/api/v1/system/health`
- Swagger vía proxy: `http://localhost:8080/docs`

## Usuarios demo

- Administrador: `admin@skysense.co` / `Admin123!`
- Operador: `operador@skysense.co` / `Operador123!`
- Mantenimiento: `mantenimiento@skysense.co` / `Mantenimiento123!`
- Consulta: `consulta@skysense.co` / `Consulta123!`

> Para un despliegue público real, desactiva `SEED_DEMO_USERS` después de crear usuarios reales y elimina/rota estas credenciales.

## Prueba MQTT

Carga las variables del `.env` en tu terminal o define al menos `MQTT_PASSWORD` y ejecuta:

```powershell
$env:MQTT_PASSWORD="TU_PASSWORD_MQTT"
python .\scripts\publish_mqtt.py 13.5
```

`13.5` m/s supera la regla demo de viento fuerte y debe crear una alerta.

## Prueba de ingesta HTTP interna

```powershell
$env:INGEST_API_KEY="TU_INGEST_API_KEY"
python .\scripts\send_demo_data.py
```

## Seguridad

Consulta `HOTFIX_V3_SECURITY_DEPLOY.md` y `DEPLOY_CHECKLIST.md`.

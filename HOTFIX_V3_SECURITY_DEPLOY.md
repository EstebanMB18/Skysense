# SkySense v3 - Security & Deploy

## Cierre de seguridad implementado

- JWT access token de corta duración (15 min por defecto).
- Refresh token JWT rotativo en cookie `HttpOnly`; su `jti` se mantiene/revoca en Redis.
- RBAC en backend (`ADMIN`, `OPERATOR`, `MAINTENANCE`, `VIEWER`).
- Contraseñas con PBKDF2-HMAC-SHA256 + salt individual.
- OTP hasheado en Redis con TTL, máximo de intentos y cooldown.
- Ingesta `/ingest/*` protegida con `X-Ingest-Key`; el navegador no recibe esta clave.
- Mosquitto sin acceso anónimo y con usuario/contraseña.
- PostgreSQL como BD de Docker; SQLite queda solo para desarrollo local.
- Redis con persistencia AOF para estado temporal.
- Auditoría de login, logout y cierre de alertas.
- Validación estricta de payloads meteorológicos con Pydantic.
- Nginx sirve React y hace proxy interno a FastAPI; backend no se publica como puerto del host.
- Cabeceras web básicas: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`.
- En `ENV=production`, la API rechaza secretos inseguros y exige Redis disponible.

## Arquitectura Docker cerrada

Browser -> Nginx/React :8080 -> FastAPI interno -> PostgreSQL / Redis
SkyNode -> Mosquitto autenticado -> MQTT Worker -> FastAPI `/ingest/*` con clave interna

El puerto MQTT 1883 se publica únicamente en `127.0.0.1` para la demostración local. Para exponer MQTT en Internet debe agregarse TLS (8883) o usar un servicio/broker administrado.

## No afirmar aún

- HTTPS público no lo genera Docker por sí solo. Para Internet se debe terminar TLS en ALB/CloudFront/Nginx con certificado.
- SES solo funciona cuando se configuran credenciales AWS y un remitente verificado. Por defecto el OTP se imprime en logs del backend (`OTP_DELIVERY_MODE=console`).
- `Base.metadata.create_all` crea el esquema inicial. Para evolución de BD de largo plazo conviene incorporar Alembic antes de múltiples releases.

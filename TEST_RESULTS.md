# Resultado de validación realizada en el entorno de generación

Fecha: 2026-11-04

## Pruebas ejecutadas
- `test_health`: PASS
- `test_login_and_stations`: PASS
- `test_ingest_latest_alert`: PASS

Resultado: **3 passed**.

## Alcance de la prueba
Se comprobó en modo demo local (SQLite):
1. Health de la API.
2. Login con JWT.
3. Consulta autenticada de estaciones.
4. Ingesta de telemetría.
5. Persistencia de la lectura.
6. Consulta de última telemetría.
7. Evaluación de regla y generación de alerta por velocidad de viento.

## No validado en este entorno
- Docker Compose, porque Docker no está disponible en el entorno de generación.
- PostgreSQL/Redis/Mosquitto reales, aunque se entregan configurados en `docker-compose.yml`.
- AWS real, porque requiere cuenta y credenciales del proyecto.
- Amazon SES real.
- Conexión al SkyNode físico.
- Build del frontend con npm, ya que el entorno no dispone de acceso externo para descargar dependencias.

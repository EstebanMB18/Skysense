# SkySense v3 - resultados de validación

Validación ejecutada antes de empaquetar:

- Backend Python: compilación sintáctica OK.
- `docker-compose.yml`: YAML válido, 6 servicios detectados.
- Pytest integración de seguridad/datos: **1 passed**.

La prueba integral cubre:

1. Health de API y base de datos.
2. Login con contraseña hasheada y JWT.
3. `/auth/me` y rol ADMIN.
4. Rechazo 401 de ingesta sin `X-Ingest-Key`.
5. Ingesta autorizada de telemetría.
6. Consulta `latest` persistida.
7. Creación de alerta por regla de viento.
8. Refresh token con cookie HttpOnly y rotación.
9. Acceso RBAC a listado de usuarios.
10. OTP generado/verificado usando el almacén temporal (Redis en Docker/producción).
11. Logout y revocación del refresh token.

Limitación del entorno de empaquetado: no dispone de daemon Docker, por lo que la ejecución de los contenedores debe validarse en Docker Desktop del equipo de despliegue. El Compose sí fue validado sintácticamente.

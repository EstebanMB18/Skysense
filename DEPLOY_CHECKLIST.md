# Checklist de despliegue SkySense v3

## Antes de levantar

- [ ] Docker Desktop operativo.
- [ ] `.env` creado desde `.env.example`.
- [ ] `JWT_SECRET` aleatorio y >= 32 caracteres.
- [ ] `INGEST_API_KEY` aleatoria y >= 24 caracteres.
- [ ] `POSTGRES_PASSWORD` aleatoria.
- [ ] `MQTT_PASSWORD` aleatoria.
- [ ] `.env` NO se sube a Git.

## Validación funcional

- [ ] Login ADMIN funciona.
- [ ] Login VIEWER no muestra Administración.
- [ ] `/auth/me` devuelve rol correcto.
- [ ] `/auth/refresh` renueva access token mediante cookie HttpOnly.
- [ ] `/ingest/telemetry` sin `X-Ingest-Key` responde 401.
- [ ] MQTT publica telemetría y el worker la persiste.
- [ ] PostgreSQL conserva datos después de reiniciar contenedores.
- [ ] OTP queda en Redis y expira.
- [ ] Histórico aparece en React.
- [ ] Viento > 12 m/s crea alerta.
- [ ] ADMIN/OPERATOR puede cerrar alerta; VIEWER no.
- [ ] Leaflet carga estaciones.
- [ ] `/system/health` reporta DB y Redis OK.

## Antes de exponer a Internet

- [ ] HTTPS/TLS configurado.
- [ ] `COOKIE_SECURE=true`.
- [ ] CORS limitado al dominio real.
- [ ] MQTT no expuesto en 1883 a Internet; usar TLS/8883 o broker administrado.
- [ ] Demo users eliminados o contraseñas rotadas.
- [ ] `OTP_DELIVERY_MODE=ses` si se requiere correo real.
- [ ] Backups PostgreSQL configurados/probados.

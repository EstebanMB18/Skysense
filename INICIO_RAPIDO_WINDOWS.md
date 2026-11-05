# Inicio rápido Windows - SkySense v3

1. Instala y abre Docker Desktop.
2. Verifica:

```powershell
docker --version
docker compose version
```

3. En la carpeta del proyecto:

```powershell
Copy-Item .env.example .env
python .\scripts\generate_secrets.py
notepad .env
```

4. Copia en `.env` los cuatro secretos generados.
5. Levanta todo:

```powershell
docker compose up --build -d
```

6. Comprueba:

```powershell
docker compose ps
```

`postgres`, `redis`, `mosquitto` y `backend` deben quedar `healthy`; `frontend` y `mqtt-worker` deben quedar `Up`.

7. Abre `http://localhost:8080`.

Si algo falla:

```powershell
docker compose logs --tail=200 backend
docker compose logs --tail=200 mosquitto
docker compose logs --tail=200 mqtt-worker
```

Para detener sin borrar datos:

```powershell
docker compose down
```

Para eliminar también BD/Redis/MQTT persistidos (solo si quieres reiniciar la demo):

```powershell
docker compose down -v
```

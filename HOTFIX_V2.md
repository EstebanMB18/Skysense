# SkySense Hotfix v2 — Frontend visual + roles + Leaflet

## Incluye
- Login real con correo y contraseña.
- 4 usuarios demo por rol: ADMIN, OPERATOR, MAINTENANCE y VIEWER.
- Endpoint `GET /api/v1/auth/me` para conocer el perfil autenticado.
- Endpoint `GET /api/v1/users` limitado a ADMIN.
- Menú dinámico por rol.
- Dashboard rediseñado con KPIs, cards, gráficas Recharts, alertas, health y selector de estación.
- Mapa Leaflet + OpenStreetMap en Resumen y Estaciones.
- Pantallas de Estaciones, Históricos, Alertas, Health y Administración.
- Botón para cerrar alertas visible solo a ADMIN y OPERATOR.
- Filtro visual para ocultar estaciones de prueba que no comienzan por `SKY-`.

## Usuarios demo
| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | admin@skysense.co | Admin123! |
| Operador | operador@skysense.co | Operador123! |
| Mantenimiento | mantenimiento@skysense.co | Mantenimiento123! |
| Consulta | consulta@skysense.co | Consulta123! |

## Aplicar sobre el proyecto actual
1. Detén backend y frontend con `Ctrl+C`.
2. Copia las carpetas `backend` y `frontend` del hotfix sobre tu proyecto actual.
3. Backend:
   ```powershell
   cd C:\Dev\SkySense_impl\backend
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. Frontend:
   ```powershell
   cd C:\Dev\SkySense_impl\frontend
   npm install
   npm run dev
   ```
5. Abre `http://localhost:5173`.

> `npm install` es importante porque el hotfix agrega `leaflet` y `react-leaflet`.

## Importante sobre la BD local existente
El seed agrega los usuarios demo faltantes aunque tu SQLite ya exista. Si antes creaste por error una estación `1`, el frontend v2 la oculta en la interfaz porque solo presenta códigos `SKY-*`. No borra datos automáticamente.

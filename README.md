# SkySense

SkySense es la plataforma de software encargada de recibir, procesar, almacenar y visualizar la información enviada por SkyNode, el prototipo físico de la estación meteorológica.

Actualmente el sistema cuenta con una arquitectura contenerizada mediante Docker y está compuesto por frontend, backend, base de datos, almacenamiento temporal, broker MQTT y un worker encargado de procesar la información enviada por los dispositivos.

---

## 1. ¿Qué hace SkySense?

SkySense permite:

- Recibir datos meteorológicos.
- Consultar temperatura, humedad, presión, velocidad del viento, dirección del viento y Density Altitude.
- Visualizar estaciones.
- Consultar históricos.
- Generar alertas.
- Consultar el estado de los servicios.
- Administrar usuarios y roles.
- Autenticar usuarios mediante usuario y contraseña.
- Proteger la API mediante JWT.
- Manejar roles y permisos mediante RBAC.
- Gestionar OTP y tokens temporales mediante Redis.
- Recibir información mediante MQTT.
- Mostrar la ubicación de estaciones utilizando Leaflet y OpenStreetMap.

Actualmente la comunicación con el prototipo real SkyNode todavía está pendiente de integración completa.

---

## 2. Arquitectura general

```text
SkyNode
   │
   │ MQTT
   ▼
Mosquitto
   │
   ▼
MQTT Worker
   │
   ▼
FastAPI
   │
   ├──────────────► PostgreSQL
   │
   ├──────────────► Redis
   │
   ▼
React + Nginx
   │
   ▼
Usuario
```

Cada componente cumple una responsabilidad diferente.

---

## 3. Explicación sencilla de cada componente

### SkyNode

SkyNode es el dispositivo físico.

Es el encargado de obtener la información de los sensores meteorológicos.

Ejemplo:

```text
Temperatura: 24.6 °C
Humedad: 66 %
Presión: 1011.8 hPa
Viento: 12.5 m/s
Dirección: 280°
```

SkyNode debe enviar esta información hacia SkySense.

Una forma sencilla de entenderlo es imaginar que SkyNode es una persona tomando mediciones en campo y enviándolas hacia una central de monitoreo.

---

### MQTT

MQTT es un protocolo de comunicación muy utilizado en Internet de las Cosas o IoT.

Permite que dispositivos como SkyNode publiquen mensajes de manera ligera.

Se puede imaginar como una radio:

```text
SkyNode habla por un canal.
Mosquitto escucha el canal.
Los sistemas interesados reciben el mensaje.
```

---

### Mosquitto

Mosquitto es el broker MQTT utilizado actualmente.

El broker funciona como intermediario entre el dispositivo y el software.

Una analogía sencilla sería una oficina de correo:

```text
SkyNode entrega una carta.
Mosquitto recibe la carta.
Mosquitto sabe a qué destinatario entregarla.
El MQTT Worker recibe la carta.
```

Mosquitto no realiza los cálculos meteorológicos.

Su responsabilidad principal es transportar los mensajes MQTT.

Actualmente el broker está protegido mediante usuario y contraseña.

---

### MQTT Worker

El MQTT Worker es un proceso que permanece escuchando los mensajes enviados a Mosquitto.

Cuando recibe información:

1. Lee el mensaje.
2. Valida su estructura.
3. Lo envía hacia el backend.
4. El backend procesa y almacena los datos.

Ejemplo:

```text
SkyNode
   ↓
Mosquitto recibe mensaje
   ↓
MQTT Worker
   ↓
FastAPI
```

El Worker puede entenderse como una persona encargada de revisar constantemente la bandeja de entrada y entregar cada mensaje al área correcta.

---

## 4. ¿Qué es una API?

Una API permite que diferentes programas se comuniquen entre ellos.

Una forma sencilla de explicarlo es utilizando el ejemplo de un restaurante.

```text
Cliente
   ↓
Mesero
   ↓
Cocina
```

El cliente quiere un plato.

Pero normalmente el cliente no entra directamente a la cocina.

El cliente le dice al mesero:

> Quiero una hamburguesa.

El mesero lleva la solicitud a la cocina.

La cocina realiza el trabajo.

Cuando el plato está listo, el mesero lo lleva nuevamente al cliente.

En un sistema:

```text
Frontend = Cliente
API = Mesero
Backend / Base de datos = Cocina
```

Por ejemplo, React puede solicitar:

```text
Dame la última temperatura de SKY-001.
```

La API recibe la solicitud, consulta la información necesaria y devuelve la respuesta.

---

## 5. FastAPI

FastAPI es el framework utilizado para desarrollar el backend de SkySense.

Está construido con Python.

FastAPI permite crear los endpoints que utiliza el sistema.

Ejemplos:

```text
GET /api/v1/stations
GET /api/v1/stations/SKY-001/latest
POST /api/v1/auth/login
```

FastAPI puede verse como el encargado de recibir las órdenes del mesero, procesarlas y decidir qué debe hacerse.

---

## 6. Backend

El backend es la parte del programa que normalmente el usuario no ve.

Realiza tareas como:

- Validar usuarios.
- Validar contraseñas.
- Generar JWT.
- Verificar roles.
- Consultar la base de datos.
- Guardar información meteorológica.
- Generar alertas.
- Procesar información recibida desde SkyNode.
- Consultar históricos.
- Gestionar estaciones.

El backend de SkySense está desarrollado principalmente con:

```text
Python
FastAPI
SQLAlchemy
```

---

## 7. Frontend

El frontend es la parte visual que utiliza el usuario.

Es lo que se muestra en el navegador.

Por ejemplo:

- Dashboard.
- Tarjetas de temperatura.
- Gráficas.
- Mapa.
- Alertas.
- Login.
- Menú.
- Administración.
- Históricos.

Puede entenderse así:

```text
Frontend = lo que el usuario ve.
Backend = lo que trabaja detrás.
```

En SkySense el frontend utiliza React.

---

## 8. React

React es la tecnología utilizada para construir la interfaz gráfica de SkySense.

React permite crear componentes reutilizables.

Ejemplo:

```text
Dashboard
├── Menú
├── Indicadores
├── Datos meteorológicos
├── Gráficas
├── Alertas
└── Mapa
```

---

## 9. Nginx

Nginx se utiliza para servir el frontend cuando el sistema está ejecutándose mediante Docker.

También funciona como intermediario entre el navegador y FastAPI.

Ejemplo:

```text
Usuario
   ↓
http://localhost:8080
   ↓
Nginx
   ├── muestra React
   └── redirige /api hacia FastAPI
```

---

## 10. PostgreSQL

PostgreSQL es la base de datos principal.

Se utiliza para almacenar información que debe conservarse.

Por ejemplo:

- Usuarios.
- Roles.
- Estaciones.
- Telemetría.
- Alertas.
- Históricos.
- Health.
- Eventos.

Puede imaginarse como un archivador organizado y permanente.

---

## 11. Redis

Redis se utiliza para guardar información temporal.

No reemplaza PostgreSQL.

En SkySense puede utilizarse para:

- OTP.
- Refresh tokens.
- TTL.
- Intentos.
- Cooldown.
- Datos temporales.

Forma sencilla de recordarlo:

```text
PostgreSQL = archivo permanente.
Redis = tablero temporal.
```

---

## 12. JWT

JWT significa JSON Web Token.

Se utiliza para identificar a un usuario autenticado.

```text
Usuario + contraseña
       ↓
FastAPI
       ↓
JWT
       ↓
Frontend
```

Después, React envía el token cuando necesita acceder a información protegida.

---

## 13. Roles y permisos

SkySense utiliza RBAC: Role-Based Access Control.

Los roles actuales son:

```text
ADMIN
OPERATOR
MAINTENANCE
VIEWER
```

Cada usuario puede acceder únicamente a las funciones permitidas por su rol.

---

## 14. Docker

Docker permite ejecutar los diferentes componentes de SkySense de manera aislada.

Actualmente Docker Compose levanta:

```text
PostgreSQL
Redis
Mosquitto
FastAPI
MQTT Worker
React + Nginx
```

Puede imaginarse como un edificio en el que cada componente tiene su propia oficina, pero todos pueden comunicarse por una red interna.

---

## 15. Servicios Docker

Al ejecutar:

```powershell
docker compose ps
```

deben aparecer:

```text
backend
frontend
mosquitto
mqtt-worker
postgres
redis
```

Idealmente:

```text
backend       healthy
mosquitto     healthy
postgres      healthy
redis         healthy
mqtt-worker   Up
frontend      Up
```

---

## 16. Requisitos para instalar SkySense

### Git

```powershell
git --version
```

### Docker Desktop

```powershell
docker --version
docker compose version
```

### Python

```powershell
python --version
```

### Navegador

Se recomienda utilizar Chrome, Edge o Firefox.

---

## 17. Descargar el proyecto

Repositorio:

```text
https://github.com/EstebanMB18/Skysense.git
```

Clonar:

```powershell
git clone https://github.com/EstebanMB18/Skysense.git
cd Skysense
```

---

## 18. Ramas Git

El proyecto utiliza tres ramas permanentes:

```text
desarrollo
pruebas
produccion
```

Flujo:

```text
desarrollo
     ↓
pruebas
     ↓
produccion
```

### desarrollo

Aquí se integran los cambios realizados por el equipo.

### pruebas

Aquí se promueven los cambios listos para validación.

### produccion

Contiene únicamente las versiones que ya fueron validadas.

No se recomienda trabajar directamente sobre `produccion`.

---

## 19. Preparar variables de entorno

SkySense utiliza variables de entorno para evitar guardar secretos directamente en el código.

```powershell
python .\scripts\prepare_env.py
```

Este script genera valores como:

```text
JWT_SECRET
INGEST_API_KEY
POSTGRES_PASSWORD
MQTT_PASSWORD
```

El archivo `.env` no debe subirse al repositorio.

---

## 20. Levantar SkySense

Desde la raíz del proyecto:

```powershell
docker compose up --build -d
```

Consultar estado:

```powershell
docker compose ps
```

---

## 21. Abrir la aplicación

Frontend:

```text
http://localhost:8080
```

Swagger:

```text
http://localhost:8080/docs
```

---

## 22. Detener el sistema

```powershell
docker compose down
```

---

## 23. Ver logs

Backend:

```powershell
docker compose logs --tail=100 backend
```

Mosquitto:

```powershell
docker compose logs --tail=100 mosquitto
```

Worker:

```powershell
docker compose logs --tail=100 mqtt-worker
```

---

## 24. Flujo completo de una medición

Cuando el prototipo SkyNode esté completamente integrado:

```text
1. Sensor mide una variable.
2. SkyNode obtiene el dato.
3. SkyNode publica por MQTT.
4. Mosquitto recibe el mensaje.
5. MQTT Worker consume el mensaje.
6. FastAPI valida y procesa.
7. PostgreSQL almacena la telemetría.
8. FastAPI expone la información por API.
9. React consulta la API.
10. El usuario visualiza el dato.
```

---

## 25. Seguridad implementada

Actualmente el sistema cuenta con:

- Usuario y contraseña.
- Contraseñas almacenadas mediante hash.
- JWT.
- Refresh token.
- RBAC.
- OTP mediante Redis.
- Protección de endpoints.
- Protección de ingesta mediante clave interna.
- Mosquitto con usuario y contraseña.
- Variables sensibles fuera del código.

---

## 26. Gestión de usuarios y recuperación de acceso

El sistema contempla la gestión completa del ciclo de vida del usuario.

Debe permitir:

- Crear usuarios desde Administración.
- Asignar roles.
- Activar o desactivar usuarios.
- Cambiar contraseña.
- Solicitar recuperación de contraseña.
- Restablecer contraseña mediante token u OTP temporal.
- Invalidar sesiones anteriores cuando se restablezca la contraseña.

### Estado actual

La gestión básica de usuarios y roles ya forma parte de la arquitectura.

Sin embargo, antes del cierre definitivo debe verificarse e implementar completamente, si todavía no está disponible en la interfaz:

```text
Crear usuario
Olvidé mi contraseña
Restablecer contraseña
Cambiar contraseña
```

El flujo esperado para recuperación es:

```text
Usuario indica correo
       ↓
Backend genera código/token temporal
       ↓
Redis almacena hash + expiración
       ↓
Usuario valida el código
       ↓
Define nueva contraseña
       ↓
PostgreSQL actualiza el hash
       ↓
Se invalidan sesiones anteriores
```

Por seguridad, el sistema no debe informar públicamente si un correo existe o no.

La respuesta recomendada es:

```text
Si el correo se encuentra registrado, recibirás instrucciones para restablecer tu contraseña.
```

---

## 27. Estado actual del proyecto

Actualmente se encuentra implementado o preparado:

- Docker Compose.
- PostgreSQL.
- Redis.
- Mosquitto.
- MQTT Worker.
- Backend FastAPI.
- Frontend React.
- Nginx.
- JWT.
- Refresh token.
- RBAC.
- OTP mediante Redis.
- Protección de ingesta.
- Dashboard.
- Alertas.
- Históricos.
- Health.
- Leaflet.
- OpenStreetMap.
- Gestión básica de estaciones.
- Flujo Git desarrollo → pruebas → produccion.

---

## 28. Qué falta para terminar el proyecto

El principal trabajo pendiente es la integración con el prototipo físico SkyNode.

### Integración real con SkyNode

SkyNode deberá:

1. Leer sensores físicos.
2. Conectarse a red.
3. Conectarse al broker MQTT.
4. Autenticarse.
5. Publicar telemetría.
6. Publicar health.
7. Publicar eventos.
8. Manejar pérdida de conectividad.
9. Recuperarse automáticamente.

### Contrato MQTT definitivo

Debe confirmarse que SkyNode publique exactamente la estructura que espera SkySense.

Ejemplo:

```json
{
  "schema_version": "1.0",
  "message_id": "MSG-SKY001-001",
  "station_id": "SKY-001",
  "timestamp_utc": "2026-11-05T12:00:00Z",
  "temperature_c": 24.6,
  "humidity_pct": 66,
  "pressure_hpa": 1011.8,
  "wind_speed_ms": 12.5,
  "wind_direction_deg": 280,
  "density_altitude_ft": 1900,
  "quality_flag": "VALID"
}
```

### Gestión de usuarios

Debe quedar validado de punta a punta:

- Crear usuario.
- Cambiar contraseña.
- Olvidé contraseña.
- Restablecer contraseña.
- Activar/desactivar usuario.

### MFA

Está pendiente integrar completamente un segundo factor como Microsoft Authenticator mediante TOTP, si se decide incluirlo en la versión final.

### HTTPS

Para una publicación externa debe configurarse HTTPS/TLS.

### Pruebas finales

Cuando SkyNode esté integrado debe validarse:

```text
Sensor real
   ↓
SkyNode
   ↓
MQTT
   ↓
Mosquitto
   ↓
MQTT Worker
   ↓
FastAPI
   ↓
PostgreSQL
   ↓
React
```

Se deben verificar:

- pérdida de paquetes;
- latencia;
- calidad de datos;
- reconexión;
- alertas;
- históricos;
- disponibilidad;
- seguridad.

---

## 29. Resumen rápido de la arquitectura

```text
SkyNode mide.

MQTT transporta.

Mosquitto recibe y distribuye.

MQTT Worker escucha y procesa mensajes.

FastAPI realiza la lógica del sistema.

PostgreSQL guarda la información permanente.

Redis guarda información temporal.

React construye la interfaz.

Nginx publica el frontend y comunica navegador con API.

Docker mantiene todos los componentes organizados.

Git controla las versiones.
```

---

## 30. Flujo Git del equipo

```text
CAMBIO NUEVO
     │
     ▼
desarrollo
     │
     │ validación inicial
     ▼
pruebas
     │
     │ pruebas completas
     ▼
produccion
```

SkySense se encuentra actualmente en etapa de integración y validación. La plataforma de software está funcional y el siguiente paso principal es conectar el flujo completo con el prototipo físico SkyNode y cerrar la gestión completa de usuarios.

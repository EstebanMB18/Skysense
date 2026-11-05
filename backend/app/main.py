from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.db.base import Base, SessionLocal, engine
from app.services.redis_store import ping as redis_ping
from app.services.seed import seed
import app.models.entities  # noqa: F401


def validate_security_config() -> None:
    if settings.ENV.lower() == "production":
        insecure = {
            "JWT_SECRET": settings.JWT_SECRET in {"change-this-secret", "demo-secret-change-me"} or len(settings.JWT_SECRET) < 32,
            "INGEST_API_KEY": settings.INGEST_API_KEY in {"change-ingest-api-key", "demo-ingest-key"} or len(settings.INGEST_API_KEY) < 24,
            "MQTT_PASSWORD": settings.MQTT_PASSWORD in {"change-mqtt-password", "skynode"} or len(settings.MQTT_PASSWORD) < 12,
        }
        bad = [k for k, v in insecure.items() if v]
        if bad:
            raise RuntimeError(f"Unsafe production configuration: {', '.join(bad)}")
        if not redis_ping():
            raise RuntimeError("Redis unavailable in production")


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_security_config()
    Base.metadata.create_all(bind=engine)
    if settings.SEED_DEMO_USERS:
        with SessionLocal() as db:
            seed(db)
    yield


app = FastAPI(
    title="SkySense API",
    version="1.1.0",
    description="Plataforma SkySense - telemetría meteorológica",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.CORS_ORIGINS.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Ingest-Key"],
)
app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {"service": "SkySense API", "docs": "/docs", "health": "/api/v1/system/health"}

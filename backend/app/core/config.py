from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "SkySense API"
    ENV: str = "local"
    DATABASE_URL: str = "sqlite:///./skysense.db"

    JWT_SECRET: str = "change-this-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 7
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    OTP_TTL_SECONDS: int = 600
    OTP_MAX_ATTEMPTS: int = 5
    OTP_COOLDOWN_SECONDS: int = 60
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_REQUIRED: bool = False

    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = "skynode"
    MQTT_PASSWORD: str = "change-mqtt-password"
    MQTT_TOPIC_ROOT: str = "skysense"
    INGEST_API_KEY: str = "change-ingest-api-key"

    OTP_DELIVERY_MODE: str = "console"  # console | ses
    AWS_REGION: str = "us-east-1"
    SES_FROM_EMAIL: str = "no-reply@example.com"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8080"
    SEED_DEMO_USERS: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

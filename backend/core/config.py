from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FarmIoT API"
    environment: str = "dev"
    secret_key: str = Field(min_length=16)
    access_token_expire_minutes: int = 30

    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "farm_iot"
    db_user: str = "postgres"
    db_password: str

    redis_url: str = "redis://redis:6379/0"
    mqtt_broker_host: str = "mqtt"
    mqtt_broker_port: int = 1883

    currency: str = "KZT"
    meat_per_kg: float = 1200.0
    owner_email: str = "owner@farmiot.local"
    owner_password: str = "changeme123"
    owner_org_id: int = 1
    command_2fa_secret: str = "JBSWY3DPEHPK3PXP"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

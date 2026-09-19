from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://expenses:expenses@localhost:5432/expenses",
        alias="DATABASE_URL",
    )
    backend_cors_origins: str = Field(
        default="http://localhost:5173",
        alias="BACKEND_CORS_ORIGINS",
    )
    frontend_url: str | None = Field(default=None, alias="FRONTEND_URL")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    allowed_hosts_value: str = Field(default="localhost,127.0.0.1", alias="ALLOWED_HOSTS")
    upload_directory: str = Field(default="uploads", alias="UPLOAD_DIR")

    model_config = SettingsConfigDict(env_file=".env", populate_by_name=True)

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin.strip().rstrip("/") for origin in self.backend_cors_origins.split(",") if origin.strip()]
        if self.frontend_url:
            origins.append(self.frontend_url.strip().rstrip("/"))
        return list(dict.fromkeys(origins))

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self.database_url

    @property
    def allowed_hosts(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts_value.split(",") if host.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_directory)


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    value = (url or "").strip()
    if not value:
        return "sqlite:///./signal.db"
    if value.startswith("postgres://"):
        value = "postgresql://" + value[len("postgres://") :]
    if value.startswith("postgresql://") and "+" not in value.split("://", 1)[0]:
        value = "postgresql+psycopg://" + value[len("postgresql://") :]
    local = "localhost" in value or "127.0.0.1" in value or value.startswith("sqlite")
    if not local and "sslmode=" not in value:
        value = f"{value}{'&' if '?' in value else '?'}sslmode=require"
    return value


def as_origin(value: str) -> str:
    origin = value.strip().rstrip("/")
    if not origin:
        return ""
    if origin.startswith("http://") or origin.startswith("https://"):
        return origin
    return f"https://{origin}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Signal"
    database_url: str = "sqlite:///./signal.db"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    frontend_url: str | None = None

    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    freshness_very_fresh_minutes: int = 10
    freshness_fresh_minutes: int = 30
    freshness_aging_minutes: int = 60
    report_expiry_minutes: int = 120

    weight_source_reliability: float = 0.25
    weight_corroboration: float = 0.25
    weight_recency: float = 0.20
    weight_location_agreement: float = 0.20
    weight_evidence_quality: float = 0.10

    avoid_confidence_threshold: float = 0.80
    avoid_min_independent_sources: int = 2
    strong_location_agreement: float = 0.75
    contradiction_penalty_max: float = 0.28

    location_cluster_meters: float = 250
    route_proximity_meters: float = 400
    corroboration_time_window_minutes: int = 45

    demo_user_id: str = "user-amara"

    @field_validator("database_url", mode="before")
    @classmethod
    def _database_url(cls, value: str) -> str:
        return normalize_database_url(value)

    @property
    def cors_origin_list(self) -> list[str]:
        origins: list[str] = []
        for raw in self.cors_origins.split(","):
            origin = as_origin(raw)
            if origin and origin not in origins:
                origins.append(origin)
        if self.frontend_url:
            origin = as_origin(self.frontend_url)
            if origin and origin not in origins:
                origins.append(origin)
        return origins

    @property
    def llm_enabled(self) -> bool:
        return bool(self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

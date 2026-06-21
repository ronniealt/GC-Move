from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/gcmove"
    REDIS_URL: str = "redis://localhost:6379"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_MAIN: str = "gpt-4o"
    OPENAI_MODEL_FAST: str = "gpt-4o-mini"

    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_SECRET_KEY: str = ""

    GOOGLE_MAPS_API_KEY: str = ""
    RESEND_API_KEY: str = ""
    SENTRY_DSN: str = ""

    APIFY_API_TOKEN: str = ""
    APIFY_REA_ACTOR_ID: str = ""
    APIFY_DOMAIN_ACTOR_ID: str = ""

    CORS_ORIGINS: str = "http://localhost:3000"
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()

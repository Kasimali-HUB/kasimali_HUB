from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are read from environment variables (or a local .env file,
    see .env.example). Never hardcode secrets here.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "GPIP - Global Payroll Intelligence Platform"
    environment: str = "development"  # development | staging | production
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://gpip:gpip@localhost:5432/gpip"

    # Country modules enabled for this deployment. Start with Netherlands only;
    # additional countries are added here as their legislation modules land.
    enabled_countries: list[str] = ["NL"]

    # Secret used to derive pseudonymized employee tokens (see app/privacy).
    # This never leaves "our systems" - the whole point is that the AI layer
    # never has it, so it can never reverse a token back to an employee.
    # MUST be overridden via env var in any real deployment; this default is
    # only for local dev / tests.
    pseudonymization_secret: str = "dev-only-change-me"


@lru_cache
def get_settings() -> Settings:
    return Settings()

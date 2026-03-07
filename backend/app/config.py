"""
UrbanPulse application configuration.

Loads settings from environment variables with sensible defaults.
Uses pydantic-settings for typed, validated configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ──────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./urbanpulse.db"

    # ── Azure OpenAI ──────────────────────────────────────────────────────
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o-2"
    azure_openai_api_version: str = "2024-12-01-preview"
    llm_provider: str = "azure_openai"

    # ── BrightData ────────────────────────────────────────────────────────
    brightdata_api_token: str = ""
    brightdata_base_url: str = "https://api.brightdata.com"

    # ── Google Places ─────────────────────────────────────────────────────
    google_places_api_key: str = ""

    # ── US Census ─────────────────────────────────────────────────────────
    census_api_key: str = ""

    # ── Montgomery ArcGIS ─────────────────────────────────────────────────
    montgomery_arcgis_base_url: str = "https://opendata.montgomeryal.gov"

    # ── CORS ──────────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        """Return CORS origins as a list of strings."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Singleton instance – import this wherever config is needed.
settings = Settings()


def get_settings() -> Settings:
    """Return the global settings instance."""
    return settings

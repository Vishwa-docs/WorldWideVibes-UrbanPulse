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

    # ── LLM / Gemini ─────────────────────────────────────────────────────
    gemini_api_key: str = ""
    llm_provider: str = "gemini"

    # ── BrightData ────────────────────────────────────────────────────────
    brightdata_api_token: str = ""
    brightdata_base_url: str = "https://api.brightdata.com"

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

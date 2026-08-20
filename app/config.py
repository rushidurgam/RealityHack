"""Load settings from environment variables / .env (never hardcode secrets)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App config. Values come from .env; see .env.example for placeholders."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "SkillBridge AI"
    app_version: str = "0.3.0"
    environment: str = "development"
    debug: bool = False

    # AI Service Settings
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_fallback_models: str = "gemini-3.6-flash,gemini-flash-latest,gemini-3.5-flash,gemini-2.5-pro"

    # Adzuna Job Intelligence Settings
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_country: str = "us"

    # Database
    database_url: str = "sqlite:///./skillbridge.db"

    # CORS & Network — include production Vercel URL + localhost for dev
    cors_origins: str = (
        "http://127.0.0.1:5173,http://localhost:5173,"
        "http://127.0.0.1:8000,http://localhost:8000,"
        "https://reality-hack.vercel.app,"
        "https://realityhack.vercel.app"
    )
    
    # Security & Guardrails
    enable_rate_limiting: bool = True
    enable_security_headers: bool = True
    enable_request_logging: bool = True
    max_upload_bytes: int = 5 * 1024 * 1024  # 5 MB
    max_pdf_pages: int = 15
    max_text_chars: int = 15000
    max_code_chars: int = 15000
    max_job_descriptions: int = 12
    external_request_timeout_seconds: float = 8.0

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a clean list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def fallback_model_list(self) -> list[str]:
        """Return fallback Gemini models list."""
        return [m.strip() for m in self.gemini_fallback_models.split(",") if m.strip()]


settings = Settings()

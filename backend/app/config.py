"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation and type safety.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings – sourced from .env or environment variables."""

    # Azure AD Service Principal
    TENANT_ID: str
    CLIENT_ID: str
    CLIENT_SECRET: str

    # Microsoft Fabric / OneLake
    WORKSPACE_NAME: str
    LAKEHOUSE_NAME: str

    # OneLake DFS endpoint (rarely needs changing)
    ONELAKE_ACCOUNT_NAME: str = "onelake"
    ONELAKE_DFS_URL: str = "https://onelake.dfs.fabric.microsoft.com"

    # Path inside the Lakehouse where PDFs are stored
    PDF_FOLDER_PATH: str = "Files/"

    # CORS – comma-separated origins allowed to call the API
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # API key placeholder for simple auth middleware (replace with real auth)
    API_KEY: str = "changeme-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()

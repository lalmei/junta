"""Environment-backed settings for CLI and applications (distinct from framework Config)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from junta._version import get_version


class JuntaEnvSettings(BaseSettings):
    """Load optional .env files for CLI and host application wiring."""

    schema_version: str = "1.0.0"
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.dev", ".env.prod"),
        env_file_encoding="utf-8",
    )
    app_name: str = "junta"
    app_description: str = "Junta: Python officer framework with Typer CLI"
    app_author: str = "Leandro G. Almeida"
    app_version: str = get_version()
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

"""Configuration management for junta."""

from pydantic import BaseModel


class Config(BaseModel):
    """Configuration model for junta."""

    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

"""Tests for configuration."""

from junta.config import Config, JuntaEnvSettings


def test_env_settings_defaults() -> None:
    """JuntaEnvSettings loads CLI-related defaults."""
    settings = JuntaEnvSettings()
    assert settings.log_format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def test_framework_config_defaults() -> None:
    """Framework Config holds Junta kernel defaults."""
    cfg = Config()
    assert cfg.version == "0.1.0"
    assert cfg.default_operator == "anthropic"
    assert cfg.tribunal_enabled is False


def test_framework_config_import() -> None:
    """Framework Config is importable from the package."""
    from junta.config.config import Config as FrameworkConfig

    c = FrameworkConfig()
    assert hasattr(c, "default_operator")

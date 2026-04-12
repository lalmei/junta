"""Rich-backed stdlib logging for the CLI (host app wiretap-style output)."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from logging import DEBUG, INFO, Formatter, Logger, getLogger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import cast

from rich.console import Console
from rich.logging import RichHandler

from junta.config import JuntaEnvSettings
from junta.utils.theme.theme import set_theme


def _is_running_in_pytest() -> bool:
    """Return True when tests are running (plain console, no ANSI)."""
    return (
        "pytest" in sys.modules
        or "PYTEST_CURRENT_TEST" in os.environ
        or any("pytest" in str(arg) for arg in sys.argv if isinstance(arg, str))
    )


def _configure_rich_log(
    name: str = "junta",
    console: Console | None = None,
    log_level: int | None = None,
    *,
    use_rotating_file_handler: bool = False,
    log_file_base_path: Path | None = None,
) -> Logger:
    """Configure a named stdlib Log with a Rich handler."""
    os.environ["NO_ALBUMENTATIONS_UPDATE"] = "1"
    if log_level is None:
        log_level = int(os.getenv("_JUNTA_LOG_LEVEL", DEBUG))
    else:
        try:
            if isinstance(log_level, str):
                log_level = int(log_level)
        except (ValueError, TypeError):
            log_level = DEBUG

    log = getLogger(name)

    if len(log.handlers) > 0:
        for handler in log.handlers:
            if handler.get_name() == "rich":
                log.setLevel(level=log_level)
                return log

    if not console:
        if _is_running_in_pytest():
            console = Console(
                file=sys.stdout,
                force_terminal=False,
                legacy_windows=False,
                no_color=True,
            )
        else:
            console = Console(theme=set_theme("dark"))

    rich_handler = RichHandler(rich_tracebacks=True, console=console)
    rich_handler.set_name("rich")
    log.addHandler(rich_handler)

    if use_rotating_file_handler and log_file_base_path is not None:
        current_date = datetime.now(tz=timezone.utc).strftime("%Y_%m_%d")
        log_file_path = log_file_base_path / f"log_{current_date}.log"
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    log.setLevel(level=log_level)
    log.propagate = False
    getLogger("PIL").setLevel(level=log_level)
    return log


def _attach_rotating_file_handler(
    log: Logger,
    log_file: str,
    maximum_log_file_size_mb: int = 10,
    maximum_log_file_time_days: int = 3,
) -> Logger:
    """Attach a rotating file handler to the given Log."""
    handler = RotatingFileHandler(
        log_file,
        maxBytes=maximum_log_file_size_mb * 1024 * 1024,
        backupCount=maximum_log_file_time_days,
    )
    handler.setFormatter(Formatter(JuntaEnvSettings().log_format))
    handler.set_name("rotating_file_handler")
    log.addHandler(handler)
    return log


def get_wiretap_console(
    name: str = "junta",
    console: Console | None = None,
    log_level: int | None = None,
) -> tuple[Logger, Console]:
    """Return a stdlib Log and Rich Console for CLI wiretap-style output."""
    if log_level is None:
        log_level = int(os.getenv("_JUNTA_LOG_LEVEL", INFO))
    else:
        try:
            if isinstance(log_level, str):
                log_level = int(log_level)
        except (ValueError, TypeError):
            log_level = INFO
    root_log = _configure_rich_log(
        use_rotating_file_handler=True,
        log_level=log_level,
    )

    if name != "junta":
        log = getLogger(name)
        log.handlers = root_log.handlers
        log.setLevel(level=root_log.level)
        log.propagate = False
    else:
        log = root_log
        if log_level != root_log.level:
            log.warning(f"Log level changed from {root_log.level} to {log_level}")
            log.setLevel(level=log_level)

    if len(root_log.handlers) > 0:
        for handler in root_log.handlers:
            if handler.get_name() == "rich":
                rich_handler: RichHandler = cast("RichHandler", handler)
                console = rich_handler.console
                return log, console

    if console is None:
        if _is_running_in_pytest():
            console = Console(
                file=sys.stdout,
                force_terminal=False,
                legacy_windows=False,
                no_color=True,
            )
        else:
            console = Console()

    return log, console


# Backward-compatible name for tests and external callers
get_logger_console = get_wiretap_console

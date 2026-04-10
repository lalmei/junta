"""junta package.

Python library with a Typer command-line interface
"""

from __future__ import annotations

from junta._version import debug_info, get_version

from junta.cli import cli
from junta.cli.main_cli import main

__all__: list[str] = ["cli", "debug_info", "get_version", "main"]
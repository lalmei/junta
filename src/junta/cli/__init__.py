"""junta CLI application module.

This package exposes the Typer-based command line interface for
`junta`.

The console script defined in `pyproject.toml` points at the package-level
`cli` object exported from `src/junta/__init__.py`,
so users can run:

```bash
junta [COMMAND] [OPTIONS]
```

or:

```bash
uv run python -m junta [COMMAND] [OPTIONS]
```

Commands are discovered dynamically from `junta/cli/commands/`.
Each command package should expose a Typer app named `app`; the registration
layer loads those subcommands automatically at startup.

Subcommands may also define a callback with `@app.callback()` to share setup or
default behavior before nested commands run.
"""

from junta.cli.main_cli import cli_app as cli

__all__: list[str] = ["cli"]

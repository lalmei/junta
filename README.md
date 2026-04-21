# Junta

[![ci](https://github.com/lalmei/junta/actions/workflows/ci.yml/badge.svg)](https://github.com/lalmei/junta/actions/workflows/ci.yml)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://lalmei.github.io/junta/)
[![pypi version](https://img.shields.io/pypi/v/junta.svg)](https://pypi.org/project/junta/)
[![license](https://img.shields.io/badge/license-ISC-blue.svg?style=flat)](LICENSE)
[![python](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg?style=flat)](#installation)
[![coverage](https://img.shields.io/endpoint?url=https://lalmei.github.io/junta/coverage-badge.json)](https://lalmei.github.io/junta/coverage/)

Junta is a Python framework for building **officers** (LLM-driven actors) with strict **doctrine** (policy), a **manifest** of **capabilities** (callable units exposed to the model), **operators** (Anthropic, OpenAI, or OpenAI-compatible Llama servers), optional **tribunal** evaluation (**rulings**), and **wiretap** observability (**intercepts**).

## Concepts

| Idea | Junta term |
|------|------------|
| Orchestrator | Junta |
| Agent | Officer |
| Roles / types | Cabinet |
| Task | Mandate |
| Conversation thread | Dossier |
| Callable unit | Capability |
| Registry | Manifest |
| LLM backend | Gringos |
| Policy | Doctrine |
| Memory / context | Intelligence |
| Prompt text assembly | Briefing |
| Model message | Dispatch |
| Capability output record | Field report |
| Event | Event |
| Configuration | Config |
| Logging / tracing | Wiretap |
| Log line | Intercept |
| Error | Breach |
| Retry / fallback | Contingency |
| Evaluation | Tribunal |
| Eval outcome | Ruling |

## Installation

```bash
pip install junta
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv add junta
```

Runtime libraries are listed in [requirements.txt](requirements.txt) and in `pyproject.toml` (`pydantic`, `anthropic`, `openai`, `httpx`, `pydantic-settings`, …).

## Quick start

1. Build a `Config` and `Junta.from_config(...)`.
2. `conscript` one or more `Operator` instances (`AnthropicOperator`, `OpenAIOperator`, `LlamaOperator`).
3. Register shared `Capability` objects on the Junta `Manifest` if needed.
4. `deploy` `Officer` subclasses from the cabinet (`Analyst`, `Executor`, …).
5. `issue` a `Mandate` to an officer codename and read the `Ruling` (when the tribunal is enabled or for the default heuristic).

See [examples/basic.py](examples/basic.py) for a minimal scripted flow (requires `ANTHROPIC_API_KEY` for a live Anthropic operator).

## CLI

The Typer CLI loads **environment settings** via `JuntaEnvSettings` (distinct from the framework `Config`). Run `junta --help` after install.

## License

ISC — see [LICENSE](LICENSE).

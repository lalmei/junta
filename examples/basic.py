"""Basic Junta example: Config, Anthropic operator, capability, Analyst, mandate, ruling."""

from __future__ import annotations

import os
import uuid

from junta import (
    Analyst,
    AnthropicOperator,
    Capability,
    CapabilityParam,
    Config,
    Junta,
    Mandate,
    Manifest,
    Ruling,
)


def echo_handler(text: str) -> str:
    return f"echo:{text}"


def main() -> Ruling:
    cfg = Config(
        default_operator="anthropic",
        tribunal_enabled=True,
    )
    junta = Junta.from_config(cfg)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        msg = "Set ANTHROPIC_API_KEY to run this example against Claude."
        raise SystemExit(msg)
    junta.conscript(AnthropicOperator(api_key=api_key))

    manifest = Manifest().register(
        Capability(
            name="echo",
            description="Echo input for demonstration.",
            params=[
                CapabilityParam(
                    name="text",
                    type="str",
                    description="Text to echo.",
                    required=True,
                )
            ],
            handler=echo_handler,
        )
    )
    junta.manifest = manifest

    analyst = Analyst(
        id=str(uuid.uuid4()),
        codename="analyst-1",
        wiretap=junta.wiretap,
    )
    junta.deploy(analyst)

    mandate = Mandate(
        id=str(uuid.uuid4()),
        briefing="Use the echo capability once with text 'Junta', then reply done.",
    )
    ruling = junta.issue(mandate, to="analyst-1")
    print(ruling.model_dump_json(indent=2))
    return ruling


if __name__ == "__main__":
    main()

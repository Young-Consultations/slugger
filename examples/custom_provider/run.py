"""Custom provider example — register and call an offline provider."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from models.provider import GenerationRequest, ProviderConfig, ProviderType
from providers.mock_provider import MockProvider
from providers.registry import ProviderRegistry


def main() -> None:
    registry = ProviderRegistry()
    provider = MockProvider(
        ProviderConfig(
            name="local-demo",
            provider_type=ProviderType.MOCK,
            model="deterministic-demo-model",
        ),
        responses=["Hello from a custom provider registration!"],
    )
    registry.register("local-demo", provider)

    resolved = registry.resolve("local-demo")
    result = resolved.generate(
        GenerationRequest(prompt="Introduce Slugger in one sentence.")
    )
    print(f"Provider: {resolved.get_metadata()['provider']}")
    print(f"Model   : {result.model}")
    print(f"Content : {result.content}")


if __name__ == "__main__":
    main()

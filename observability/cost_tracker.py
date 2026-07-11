"""LLM cost tracker — record and aggregate provider API call costs.

:class:`CostTracker` accumulates token-usage events emitted by LLM providers
and computes total and per-model costs using configurable price tables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Default price table: (provider, model) → (input $/1K tokens, output $/1K tokens)
DEFAULT_PRICES: dict[tuple[str, str], tuple[float, float]] = {
    ('openai', 'gpt-4o'): (0.005, 0.015),
    ('openai', 'gpt-4o-mini'): (0.00015, 0.0006),
    ('openai', 'gpt-4'): (0.03, 0.06),
    ('openai', 'gpt-3.5-turbo'): (0.0005, 0.0015),
    ('anthropic', 'claude-3-5-sonnet-20241022'): (0.003, 0.015),
    ('anthropic', 'claude-3-haiku-20240307'): (0.00025, 0.00125),
    ('mock', 'mock-model'): (0.0, 0.0),
}


@dataclass
class UsageRecord:
    """A single LLM API call record.

    Parameters
    ----------
    provider:
        Provider name (e.g. ``'openai'``).
    model:
        Model name (e.g. ``'gpt-4o'``).
    input_tokens:
        Number of prompt tokens consumed.
    output_tokens:
        Number of completion tokens generated.
    agent_name:
        Agent that triggered the call.
    step_name:
        Workflow step during which the call occurred.
    cost_usd:
        Computed cost in USD (populated by :class:`CostTracker`).
    metadata:
        Arbitrary annotations.
    """

    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    agent_name: str = ''
    step_name: str = ''
    cost_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'provider': self.provider,
            'model': self.model,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'agent_name': self.agent_name,
            'step_name': self.step_name,
            'cost_usd': self.cost_usd,
        }


class CostTracker:
    """Accumulate and report LLM API call costs.

    Parameters
    ----------
    prices:
        Mapping of ``(provider, model)`` to ``(input_per_1k, output_per_1k)``
        USD rates.  Defaults to :data:`DEFAULT_PRICES`.

    Examples
    --------
    >>> tracker = CostTracker()
    >>> tracker.record('openai', 'gpt-4o', input_tokens=1000, output_tokens=500)
    >>> tracker.total_cost()
    0.012500
    """

    def __init__(self, prices: dict[tuple[str, str], tuple[float, float]] | None = None) -> None:
        self._prices = prices if prices is not None else DEFAULT_PRICES
        self._records: list[UsageRecord] = []

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        agent_name: str = '',
        step_name: str = '',
        metadata: dict[str, Any] | None = None,
    ) -> UsageRecord:
        """Create and store a usage record.

        Returns the record with :attr:`UsageRecord.cost_usd` populated.
        """
        in_rate, out_rate = self._prices.get((provider, model), (0.0, 0.0))
        cost = (input_tokens / 1000) * in_rate + (output_tokens / 1000) * out_rate
        record = UsageRecord(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            agent_name=agent_name,
            step_name=step_name,
            cost_usd=round(cost, 8),
            metadata=metadata or {},
        )
        self._records.append(record)
        return record

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def total_cost(self) -> float:
        """Return the total cost in USD across all records."""
        return round(sum(r.cost_usd for r in self._records), 8)

    def total_tokens(self) -> dict[str, int]:
        """Return total input and output token counts."""
        return {
            'input': sum(r.input_tokens for r in self._records),
            'output': sum(r.output_tokens for r in self._records),
        }

    def cost_by_model(self) -> dict[str, float]:
        """Return cost grouped by ``provider/model`` key."""
        result: dict[str, float] = {}
        for r in self._records:
            key = f'{r.provider}/{r.model}'
            result[key] = round(result.get(key, 0.0) + r.cost_usd, 8)
        return result

    def cost_by_agent(self) -> dict[str, float]:
        """Return cost grouped by agent name."""
        result: dict[str, float] = {}
        for r in self._records:
            key = r.agent_name or 'unknown'
            result[key] = round(result.get(key, 0.0) + r.cost_usd, 8)
        return result

    def summary(self) -> dict[str, Any]:
        """Return a full cost summary dict."""
        return {
            'total_cost_usd': self.total_cost(),
            'total_tokens': self.total_tokens(),
            'by_model': self.cost_by_model(),
            'by_agent': self.cost_by_agent(),
            'record_count': len(self._records),
        }

    def records(self) -> list[UsageRecord]:
        """Return all usage records."""
        return list(self._records)

    def reset(self) -> None:
        """Clear all accumulated records."""
        self._records.clear()

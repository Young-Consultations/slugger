"""Token budgeting — enforce token-usage limits per run, step, or agent.

:class:`TokenBudget` tracks consumed tokens against declared budgets and raises
:class:`BudgetExceededError` (or records a warning) when limits are breached.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class BudgetExceededError(Exception):
    """Raised when a token budget is exceeded."""


@dataclass
class BudgetAllocation:
    """A declared token budget for a named scope.

    Parameters
    ----------
    scope:
        Budget scope identifier (e.g. ``'run'``, ``'step:code_generation'``,
        ``'agent:requirements_agent'``).
    max_input_tokens:
        Maximum allowed input tokens.  ``None`` means unlimited.
    max_output_tokens:
        Maximum allowed output tokens.  ``None`` means unlimited.
    max_total_tokens:
        Maximum combined tokens.  ``None`` means unlimited.
    """

    scope: str
    max_input_tokens: int | None = None
    max_output_tokens: int | None = None
    max_total_tokens: int | None = None


@dataclass
class BudgetUsage:
    """Accumulated token usage for a scope."""

    scope: str
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
        }


class TokenBudget:
    """Track token consumption and enforce declared budgets.

    Parameters
    ----------
    strict:
        When ``True``, breaching a budget raises :class:`BudgetExceededError`.
        When ``False``, a budget breach only records an overflow flag.

    Examples
    --------
    >>> budget = TokenBudget()
    >>> budget.allocate(BudgetAllocation('run', max_total_tokens=10_000))
    >>> budget.consume('run', input_tokens=3_000, output_tokens=2_000)
    >>> budget.remaining('run')
    {'input': None, 'output': None, 'total': 5000}
    """

    def __init__(self, strict: bool = True) -> None:
        self.strict = strict
        self._allocations: dict[str, BudgetAllocation] = {}
        self._usage: dict[str, BudgetUsage] = {}
        self._overflows: list[str] = []

    # ------------------------------------------------------------------
    # Budget management
    # ------------------------------------------------------------------

    def allocate(self, allocation: BudgetAllocation) -> None:
        """Declare a token budget for *allocation.scope*."""
        self._allocations[allocation.scope] = allocation
        self._usage.setdefault(allocation.scope, BudgetUsage(scope=allocation.scope))

    # ------------------------------------------------------------------
    # Consumption
    # ------------------------------------------------------------------

    def consume(
        self,
        scope: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> BudgetUsage:
        """Record token consumption for *scope*.

        Raises
        ------
        BudgetExceededError
            In strict mode when any limit is breached.

        Returns
        -------
        BudgetUsage
            Updated usage record.
        """
        usage = self._usage.setdefault(scope, BudgetUsage(scope=scope))
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens

        allocation = self._allocations.get(scope)
        if allocation:
            violations: list[str] = []
            if (
                allocation.max_input_tokens is not None
                and usage.input_tokens > allocation.max_input_tokens
            ):
                violations.append(
                    f"Input token budget exceeded for '{scope}': "
                    f"{usage.input_tokens} > {allocation.max_input_tokens}"
                )
            if (
                allocation.max_output_tokens is not None
                and usage.output_tokens > allocation.max_output_tokens
            ):
                violations.append(
                    f"Output token budget exceeded for '{scope}': "
                    f"{usage.output_tokens} > {allocation.max_output_tokens}"
                )
            if (
                allocation.max_total_tokens is not None
                and usage.total_tokens > allocation.max_total_tokens
            ):
                violations.append(
                    f"Total token budget exceeded for '{scope}': "
                    f"{usage.total_tokens} > {allocation.max_total_tokens}"
                )
            if violations:
                self._overflows.extend(violations)
                if self.strict:
                    raise BudgetExceededError("\n".join(violations))

        return usage

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def remaining(self, scope: str) -> dict[str, int | None]:
        """Return remaining budget for *scope*.

        Values are ``None`` when no limit is declared for that dimension.
        """
        usage = self._usage.get(scope, BudgetUsage(scope=scope))
        allocation = self._allocations.get(scope)

        def _rem(limit: int | None, used: int) -> int | None:
            return max(0, limit - used) if limit is not None else None

        return {
            "input": _rem(
                allocation.max_input_tokens if allocation else None, usage.input_tokens
            ),
            "output": _rem(
                allocation.max_output_tokens if allocation else None,
                usage.output_tokens,
            ),
            "total": _rem(
                allocation.max_total_tokens if allocation else None, usage.total_tokens
            ),
        }

    def usage(self, scope: str) -> BudgetUsage:
        """Return accumulated usage for *scope*."""
        return self._usage.get(scope, BudgetUsage(scope=scope))

    def all_usage(self) -> list[BudgetUsage]:
        """Return usage for all scopes."""
        return list(self._usage.values())

    def overflows(self) -> list[str]:
        """Return all recorded budget-overflow messages."""
        return list(self._overflows)

    def summary(self) -> dict[str, Any]:
        """Return a full budget summary."""
        return {
            "scopes": [u.to_dict() for u in self._usage.values()],
            "overflows": self._overflows,
            "total_input_tokens": sum(u.input_tokens for u in self._usage.values()),
            "total_output_tokens": sum(u.output_tokens for u in self._usage.values()),
        }

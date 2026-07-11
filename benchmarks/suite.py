"""Benchmark suite — measure and compare agent and workflow performance.

:class:`BenchmarkSuite` runs named benchmark functions, collects timing and
token-usage statistics, and produces structured reports suitable for CI
performance budgets or trend tracking.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class BenchmarkResult:
    """Outcome of a single benchmark run.

    Parameters
    ----------
    name:
        Benchmark name.
    elapsed_ms:
        Wall-clock time in milliseconds.
    iterations:
        Number of times the benchmark function was called.
    avg_ms:
        Average elapsed time per iteration.
    metadata:
        Arbitrary annotations produced by the benchmark function.
    error:
        If set, the benchmark raised an exception.
    """

    name: str
    elapsed_ms: float
    iterations: int
    avg_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str = ''

    @property
    def passed(self) -> bool:
        return not self.error

    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'elapsed_ms': round(self.elapsed_ms, 3),
            'iterations': self.iterations,
            'avg_ms': round(self.avg_ms, 3),
            'passed': self.passed,
            'error': self.error,
            'metadata': self.metadata,
        }


@dataclass
class BudgetSpec:
    """Performance budget for a benchmark.

    Parameters
    ----------
    benchmark_name:
        Name of the benchmark this budget applies to.
    max_avg_ms:
        Maximum allowable average execution time per iteration in milliseconds.
    """

    benchmark_name: str
    max_avg_ms: float


class BenchmarkSuite:
    """Register and run benchmarks with optional performance budgets.

    Parameters
    ----------
    iterations:
        Default number of iterations per benchmark.

    Examples
    --------
    >>> suite = BenchmarkSuite()
    >>> suite.register('parse_yaml', lambda: WorkflowParser().parse_file(path), iterations=50)
    >>> results = suite.run_all()
    >>> results[0].avg_ms
    1.4
    """

    def __init__(self, iterations: int = 10) -> None:
        self._default_iterations = iterations
        self._benchmarks: dict[str, tuple[Callable[[], Any], int]] = {}
        self._budgets: dict[str, BudgetSpec] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        fn: Callable[[], Any],
        iterations: int | None = None,
    ) -> None:
        """Register a benchmark function.

        Parameters
        ----------
        name:
            Unique benchmark name.
        fn:
            Zero-argument callable to benchmark.
        iterations:
            Override the default iteration count.
        """
        self._benchmarks[name] = (fn, iterations if iterations is not None else self._default_iterations)

    def set_budget(self, budget: BudgetSpec) -> None:
        """Declare a performance budget for a benchmark."""
        self._budgets[budget.benchmark_name] = budget

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(self, name: str) -> BenchmarkResult:
        """Run the benchmark named *name* and return its result.

        Raises
        ------
        KeyError
            If *name* is not registered.
        """
        fn, iters = self._benchmarks[name]
        start = time.perf_counter()
        error = ''
        metadata: dict[str, Any] = {}
        try:
            for _ in range(iters):
                result = fn()
                if isinstance(result, dict):
                    metadata.update(result)
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
        elapsed_ms = (time.perf_counter() - start) * 1000
        avg_ms = elapsed_ms / max(iters, 1)
        return BenchmarkResult(
            name=name,
            elapsed_ms=elapsed_ms,
            iterations=iters,
            avg_ms=avg_ms,
            metadata=metadata,
            error=error,
        )

    def run_all(self) -> list[BenchmarkResult]:
        """Run all registered benchmarks and return results."""
        return [self.run(name) for name in self._benchmarks]

    # ------------------------------------------------------------------
    # Budget evaluation
    # ------------------------------------------------------------------

    def check_budgets(self, results: list[BenchmarkResult]) -> dict[str, Any]:
        """Evaluate *results* against declared budgets.

        Returns
        -------
        dict
            ``{'passed': bool, 'violations': list[str]}``
        """
        violations: list[str] = []
        result_map = {r.name: r for r in results}
        for name, budget in self._budgets.items():
            result = result_map.get(name)
            if result and result.avg_ms > budget.max_avg_ms:
                violations.append(
                    f"'{name}': avg {result.avg_ms:.1f}ms exceeds budget {budget.max_avg_ms:.1f}ms"
                )
        return {'passed': not violations, 'violations': violations}

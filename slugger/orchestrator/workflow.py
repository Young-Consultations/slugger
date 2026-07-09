"""A minimal workflow engine supporting sequential execution, retries and
progress tracking.

The engine is intentionally small but extensible. It accepts steps as callables
(or Agent instances) and runs them in order. Each step receives a shared
context dict and may mutate it. The engine returns the final context.
"""
from typing import Any, Callable, Dict, List, Optional
import time


class StepExecutionError(Exception):
    pass


class WorkflowEngine:
    def __init__(self) -> None:
        self.progress: List[Dict[str, Any]] = []

    def run_sequential(self, steps: List[Callable[[Dict[str, Any]], Dict[str, Any]]],
                       context: Optional[Dict[str, Any]] = None,
                       retry: int = 0) -> Dict[str, Any]:
        context = context or {}
        for index, step in enumerate(steps):
            step_name = getattr(step, "__name__", getattr(step, "name", f"step_{index}"))
            attempt = 0
            last_exc: Optional[Exception] = None
            while attempt <= retry:
                try:
                    start = time.time()
                    result = step(context)
                    duration = time.time() - start
                    self.progress.append({"step": step_name, "status": "success", "duration": duration})
                    # merge result into context (prefer explicit keys from result)
                    if isinstance(result, dict):
                        context.update(result)
                    break
                except Exception as exc:  # pragma: no cover - exercised in tests
                    last_exc = exc
                    attempt += 1
                    self.progress.append({"step": step_name, "status": "retry", "attempt": attempt})
                    time.sleep(0.1)
            else:
                # exhausted retries
                raise StepExecutionError(f"Step '{step_name}' failed after {retry} retries") from last_exc
        return context


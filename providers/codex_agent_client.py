"""Codex coding-agent adapter interface and deterministic fake.

ADR-005 selects the controlled ``codex exec`` adapter pattern.  A thin
``ICodexAgentClient`` contract wraps the Codex CLI or SDK so that all
workspace-level code-generation, review, and refactoring tasks are routed
through a single, permission-aware, auditable surface.

The ``FakeCodexAgentClient`` provides fully deterministic test behaviour
without network access or a real Codex process.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_within(resolved_path: Path, allowed: Path) -> bool:
    """Return True if *resolved_path* is within *allowed* (after resolving *allowed*)."""
    try:
        resolved_path.relative_to(allowed.resolve())
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

class CodexEventType(str, Enum):
    """Types of events emitted by the Codex agent."""
    FILE_WRITE = 'file_write'
    FILE_READ = 'file_read'
    COMMAND_RUN = 'command_run'
    TASK_COMPLETE = 'task_complete'
    REVIEW_FINDING = 'review_finding'
    ERROR = 'error'


@dataclass
class CodexEvent:
    """A single event emitted during a Codex agent session."""
    event_type: CodexEventType
    payload: dict[str, object] = field(default_factory=dict)
    session_id: str = ''


@dataclass
class FileChange:
    """A file modification produced by the Codex agent."""
    path: str
    content: str
    operation: str = 'write'  # write | delete


@dataclass
class ReviewFinding:
    """A single finding from a Codex code review."""
    severity: str  # critical | high | medium | low | info
    message: str
    file_path: str = ''
    line: int | None = None


@dataclass
class CodexTaskResult:
    """Structured result returned when a Codex task completes."""
    session_id: str
    success: bool
    file_changes: list[FileChange] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    findings: list[ReviewFinding] = field(default_factory=list)
    unresolved_issues: list[str] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    summary: str = ''


@dataclass
class CodexWorkspace:
    """A disposable, permission-scoped workspace for Codex agent execution."""
    root: Path
    allowed_commands: list[str] = field(default_factory=lambda: ['python', 'pip', 'pytest'])
    write_allowed_paths: list[str] = field(default_factory=list)
    timeout_seconds: int = 120

    def is_path_allowed(self, path: str) -> bool:
        """Return True if *path* is within an allowed write location."""
        resolved = Path(path).resolve()
        if not self.write_allowed_paths:
            # Default: allow anything within root
            try:
                resolved.relative_to(self.root.resolve())
                return True
            except ValueError:
                return False
        return any(
            _is_within(resolved, Path(allowed))
            for allowed in self.write_allowed_paths
        )

    def is_command_allowed(self, command: str) -> bool:
        """Return True if the leading command token is allowed."""
        cmd_token = command.split()[0] if command.strip() else ''
        return cmd_token in self.allowed_commands


# ---------------------------------------------------------------------------
# Abstract contract
# ---------------------------------------------------------------------------

class ICodexAgentClient(ABC):
    """Contract for the Codex coding-agent adapter.

    Implementations must support stateful workspace-level code tasks with
    explicit session IDs for auditability and resume.
    """

    @abstractmethod
    def start_task(
        self,
        task_brief: str,
        workspace: CodexWorkspace,
        *,
        session_id: str | None = None,
        context_files: list[str] | None = None,
    ) -> CodexTaskResult:
        """Start a new Codex task and return the completed result."""

    @abstractmethod
    def continue_task(
        self,
        session_id: str,
        follow_up: str,
        workspace: CodexWorkspace,
    ) -> CodexTaskResult:
        """Continue an existing session with a follow-up instruction."""

    @abstractmethod
    def review(
        self,
        code: str,
        *,
        language: str = 'Python',
        criteria: list[str] | None = None,
        session_id: str | None = None,
    ) -> CodexTaskResult:
        """Perform a structured code review and return prioritised findings."""

    @abstractmethod
    def retrieve_events(self, session_id: str) -> list[CodexEvent]:
        """Return all events recorded for *session_id*."""

    @abstractmethod
    def terminate(self, session_id: str) -> None:
        """Terminate an active session and release workspace resources."""


# ---------------------------------------------------------------------------
# Deterministic fake for tests
# ---------------------------------------------------------------------------

class FakeCodexAgentClient(ICodexAgentClient):
    """Deterministic fake Codex agent for testing — no network required.

    Callers can configure canned responses and inspect recorded calls.
    """

    def __init__(
        self,
        default_code: str = '# generated by FakeCodexAgent\nprint("hello")\n',
        default_findings: list[ReviewFinding] | None = None,
    ) -> None:
        self.default_code = default_code
        self.default_findings: list[ReviewFinding] = default_findings or [
            ReviewFinding(severity='info', message='No issues found.'),
        ]
        self._sessions: dict[str, list[CodexEvent]] = {}
        self.calls: list[dict[str, object]] = []
        self._session_counter = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _new_session(self, session_id: str | None) -> str:
        sid = session_id or f'fake-session-{self._session_counter}'
        self._session_counter += 1
        self._sessions.setdefault(sid, [])
        return sid

    # ------------------------------------------------------------------
    # ICodexAgentClient
    # ------------------------------------------------------------------

    def start_task(
        self,
        task_brief: str,
        workspace: CodexWorkspace,
        *,
        session_id: str | None = None,
        context_files: list[str] | None = None,
    ) -> CodexTaskResult:
        sid = self._new_session(session_id)
        self.calls.append({'method': 'start_task', 'task_brief': task_brief, 'session_id': sid})
        change_path = str(workspace.root / 'generated.py')
        file_change = FileChange(path=change_path, content=self.default_code)
        event = CodexEvent(
            event_type=CodexEventType.FILE_WRITE,
            payload={'path': change_path},
            session_id=sid,
        )
        complete_event = CodexEvent(
            event_type=CodexEventType.TASK_COMPLETE,
            payload={'summary': 'Task complete'},
            session_id=sid,
        )
        self._sessions[sid].extend([event, complete_event])
        return CodexTaskResult(
            session_id=sid,
            success=True,
            file_changes=[file_change],
            commands_run=['python generated.py'],
            summary=f'Generated code for: {task_brief[:80]}',
            input_tokens=len(task_brief.split()),
            output_tokens=len(self.default_code.split()),
        )

    def continue_task(
        self,
        session_id: str,
        follow_up: str,
        workspace: CodexWorkspace,
    ) -> CodexTaskResult:
        sid = self._new_session(session_id)
        self.calls.append({'method': 'continue_task', 'session_id': sid, 'follow_up': follow_up})
        return CodexTaskResult(
            session_id=sid,
            success=True,
            summary=f'Continued: {follow_up[:60]}',
        )

    def review(
        self,
        code: str,
        *,
        language: str = 'Python',
        criteria: list[str] | None = None,
        session_id: str | None = None,
    ) -> CodexTaskResult:
        sid = self._new_session(session_id)
        self.calls.append({'method': 'review', 'language': language, 'session_id': sid})
        events = [
            CodexEvent(
                event_type=CodexEventType.REVIEW_FINDING,
                payload={'severity': f.severity, 'message': f.message},
                session_id=sid,
            )
            for f in self.default_findings
        ]
        self._sessions[sid].extend(events)
        return CodexTaskResult(
            session_id=sid,
            success=True,
            findings=list(self.default_findings),
            summary=f'Review complete. {len(self.default_findings)} finding(s).',
        )

    def retrieve_events(self, session_id: str) -> list[CodexEvent]:
        self.calls.append({'method': 'retrieve_events', 'session_id': session_id})
        return list(self._sessions.get(session_id, []))

    def terminate(self, session_id: str) -> None:
        self.calls.append({'method': 'terminate', 'session_id': session_id})
        self._sessions.pop(session_id, None)

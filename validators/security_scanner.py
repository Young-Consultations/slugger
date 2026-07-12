"""Security scanner — static analysis of artifact content for common security issues.

:class:`SecurityScanner` checks artifact text for hard-coded credentials,
dangerous function calls, and other common security anti-patterns.  It is
intentionally lightweight and pattern-based; for deep analysis use dedicated
tools (Bandit, Semgrep, etc.).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Finding severity level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityFinding:
    """A single security issue detected in an artifact.

    Parameters
    ----------
    rule_id:
        Identifier of the rule that fired.
    severity:
        Severity level.
    message:
        Human-readable description of the issue.
    line_number:
        Approximate line where the issue was found (1-based), or 0 if unknown.
    snippet:
        The matched text fragment (truncated).
    """

    rule_id: str
    severity: Severity
    message: str
    line_number: int = 0
    snippet: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message,
            "line_number": self.line_number,
            "snippet": self.snippet[:120],
        }


@dataclass
class ScanResult:
    """Aggregate result of a security scan."""

    artifact_name: str
    findings: list[SecurityFinding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """``True`` when no CRITICAL or HIGH findings exist."""
        return not any(
            f.severity in (Severity.CRITICAL, Severity.HIGH) for f in self.findings
        )

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_name": self.artifact_name,
            "passed": self.passed,
            "finding_count": self.finding_count,
            "findings": [f.to_dict() for f in self.findings],
        }


# --------------------------------------------------------------------------- #
# Built-in rules                                                               #
# --------------------------------------------------------------------------- #


@dataclass
class _Rule:
    rule_id: str
    severity: Severity
    pattern: re.Pattern[str]
    message: str


_RULES: list[_Rule] = [
    _Rule(
        "SEC001",
        Severity.CRITICAL,
        re.compile(r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{4,}["\']'),
        "Hard-coded password detected",
    ),
    _Rule(
        "SEC002",
        Severity.CRITICAL,
        re.compile(r'(?i)(api[_-]?key|apikey)\s*=\s*["\'][A-Za-z0-9_\-]{10,}["\']'),
        "Hard-coded API key detected",
    ),
    _Rule(
        "SEC003",
        Severity.CRITICAL,
        re.compile(r'(?i)(secret[_-]?key|secret)\s*=\s*["\'][A-Za-z0-9_\-]{8,}["\']'),
        "Hard-coded secret detected",
    ),
    _Rule(
        "SEC004",
        Severity.HIGH,
        re.compile(
            r'(?i)(access[_-]?token|auth[_-]?token)\s*=\s*["\'][A-Za-z0-9_\-.]{10,}["\']'
        ),
        "Hard-coded token detected",
    ),
    _Rule(
        "SEC005",
        Severity.HIGH,
        re.compile(r"\beval\s*\("),
        "Use of eval() — potential code injection",
    ),
    _Rule(
        "SEC006",
        Severity.HIGH,
        re.compile(r"\bexec\s*\("),
        "Use of exec() — potential code injection",
    ),
    _Rule(
        "SEC007",
        Severity.MEDIUM,
        re.compile(r'\bsubprocess\.call\s*\(\s*["\']'),
        "subprocess.call with string argument — prefer list form",
    ),
    _Rule(
        "SEC008",
        Severity.MEDIUM,
        re.compile(r"\bos\.system\s*\("),
        "os.system() — prefer subprocess with a list",
    ),
    _Rule(
        "SEC009",
        Severity.LOW,
        re.compile(r"\bprint\s*\(.*password", re.IGNORECASE),
        "Possible password logging",
    ),
    _Rule(
        "SEC010",
        Severity.INFO,
        re.compile(r"\bTODO\s*:.*(?:auth|security|cred)", re.IGNORECASE),
        "Security-related TODO comment",
    ),
]


# --------------------------------------------------------------------------- #
# Scanner                                                                      #
# --------------------------------------------------------------------------- #


class SecurityScanner:
    """Scan artifact text for security issues using pattern-based rules.

    Parameters
    ----------
    extra_rules:
        Additional :class:`_Rule` objects to include alongside the built-ins.

    Examples
    --------
    >>> scanner = SecurityScanner()
    >>> result = scanner.scan('my_artifact', 'password = "hunter2"')
    >>> result.passed
    False
    """

    def __init__(self, extra_rules: list[_Rule] | None = None) -> None:
        self._rules = list(_RULES) + (extra_rules or [])

    def scan(self, artifact_name: str, content: str) -> ScanResult:
        """Scan *content* for security issues.

        Parameters
        ----------
        artifact_name:
            Name of the artifact (used for reporting).
        content:
            Text content to scan.

        Returns
        -------
        ScanResult
        """
        findings: list[SecurityFinding] = []
        lines = content.splitlines()

        for rule in self._rules:
            for line_no, line in enumerate(lines, start=1):
                match = rule.pattern.search(line)
                if match:
                    findings.append(
                        SecurityFinding(
                            rule_id=rule.rule_id,
                            severity=rule.severity,
                            message=rule.message,
                            line_number=line_no,
                            snippet=line.strip()[:120],
                        )
                    )

        return ScanResult(artifact_name=artifact_name, findings=findings)

    def scan_many(self, artifacts: dict[str, str]) -> list[ScanResult]:
        """Scan multiple artifacts.

        Parameters
        ----------
        artifacts:
            Mapping of artifact name → content.

        Returns
        -------
        list[ScanResult]
        """
        return [self.scan(name, content) for name, content in artifacts.items()]

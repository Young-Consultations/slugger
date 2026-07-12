"""Bounded code-review, QA, and security remediation loops (CC-010).

Normalizes findings from code review, tests, linting, and security scans
into a single model.  Tracks the lifecycle of each finding through
detection, attempted remediation, and final disposition.

Findings with critical/high security severity cannot be auto-waived.
Non-converging remediation ends in `manual_intervention_required`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

from core.exceptions import RemediationExhaustedError

_LOG = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Finding domain models
# ---------------------------------------------------------------------------


class FindingSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(str, Enum):
    CODE_REVIEW = "code_review"
    TEST_FAILURE = "test_failure"
    LINT = "lint"
    TYPE_CHECK = "type_check"
    SECURITY = "security"
    DEPENDENCY = "dependency"
    COVERAGE = "coverage"


class FindingStatus(str, Enum):
    OPEN = "open"
    REMEDIATED = "remediated"
    WAIVED = "waived"
    ESCALATED = "escalated"
    MANUAL_REQUIRED = "manual_intervention_required"


@dataclass
class Finding:
    """A normalized finding from any review or quality gate."""

    finding_id: str
    severity: FindingSeverity
    category: FindingCategory
    message: str
    file_path: str = ""
    line: int | None = None
    requirement_ids: list[str] = field(default_factory=list)
    evidence_id: str = ""
    remediation_guidance: str = ""
    waiver_eligible: bool = True
    status: FindingStatus = FindingStatus.OPEN
    attempt_count: int = 0

    @property
    def is_blocking(self) -> bool:
        """Return True if this finding blocks delivery."""
        return self.severity in (FindingSeverity.CRITICAL, FindingSeverity.HIGH)

    @property
    def is_security_finding(self) -> bool:
        return self.category == FindingCategory.SECURITY

    @property
    def requires_human_waiver(self) -> bool:
        """Security findings at critical/high cannot be auto-waived."""
        return self.is_security_finding and self.severity in (
            FindingSeverity.CRITICAL,
            FindingSeverity.HIGH,
        )


# ---------------------------------------------------------------------------
# Bounds per category
# ---------------------------------------------------------------------------

DEFAULT_MAX_ATTEMPTS: dict[FindingCategory, int] = {
    FindingCategory.CODE_REVIEW: 3,
    FindingCategory.TEST_FAILURE: 3,
    FindingCategory.LINT: 2,
    FindingCategory.TYPE_CHECK: 2,
    FindingCategory.SECURITY: 2,
    FindingCategory.DEPENDENCY: 1,
    FindingCategory.COVERAGE: 1,
}


# ---------------------------------------------------------------------------
# Remediation loop
# ---------------------------------------------------------------------------


@dataclass
class RemediationAttempt:
    """Records a single remediation attempt for a finding."""

    attempt_number: int
    finding_id: str
    action_taken: str
    result: str
    success: bool
    file_versions: dict[str, str] = field(default_factory=dict)


@dataclass
class RemediationLoopResult:
    """Final result of a bounded remediation loop."""

    all_resolved: bool
    open_findings: list[Finding] = field(default_factory=list)
    resolved_findings: list[Finding] = field(default_factory=list)
    waived_findings: list[Finding] = field(default_factory=list)
    escalated_findings: list[Finding] = field(default_factory=list)
    attempts: list[RemediationAttempt] = field(default_factory=list)
    requires_manual_intervention: bool = False
    status: str = "completed"
    exhausted_error: RemediationExhaustedError | None = None


class BoundedRemediationLoop:
    """Run bounded remediation attempts for a set of findings.

    Each finding category has a maximum number of attempts.  Critical and
    high security findings require explicit human approval to waive —
    they can never be auto-waived.  Non-converging findings are escalated.
    """

    def __init__(
        self,
        max_attempts: int | dict[FindingCategory, int] | None = None,
    ) -> None:
        self._default_max_attempts = 3
        self._max_attempts_by_category = dict(DEFAULT_MAX_ATTEMPTS)
        if isinstance(max_attempts, int):
            self._default_max_attempts = max_attempts
            self._max_attempts_by_category = {
                category: max_attempts for category in DEFAULT_MAX_ATTEMPTS
            }
        elif isinstance(max_attempts, dict):
            self._max_attempts_by_category.update(max_attempts)
        elif max_attempts is not None:
            raise TypeError("max_attempts must be an int, a category map, or None")

    def process(
        self,
        findings: list[Finding],
        attempt_fn: object | None = None,
    ) -> RemediationLoopResult:
        """Process findings through bounded remediation attempts.

        Parameters
        ----------
        findings:
            All findings to process.
        attempt_fn:
            Optional callable(finding) → bool that tries to remediate.
            If None, findings are only classified, not remediated.
        """
        result = RemediationLoopResult(all_resolved=True)
        attempt_number = 0

        for finding in findings:
            max_att = self._max_attempts_by_category.get(
                finding.category, self._default_max_attempts
            )
            resolved = False

            if attempt_fn is not None:
                for att_idx in range(max_att):
                    attempt_number += 1
                    finding.attempt_count += 1
                    try:
                        success = bool(attempt_fn(finding))
                    except Exception as exc:  # noqa: BLE001
                        _LOG.warning(
                            "Remediation attempt %d for finding %r raised: %s: %s",
                            att_idx + 1,
                            finding.finding_id,
                            type(exc).__name__,
                            exc,
                        )
                        success = False
                    attempt = RemediationAttempt(
                        attempt_number=attempt_number,
                        finding_id=finding.finding_id,
                        action_taken=f"attempt_{att_idx + 1}",
                        result="resolved" if success else "failed",
                        success=success,
                    )
                    result.attempts.append(attempt)
                    if success:
                        finding.status = FindingStatus.REMEDIATED
                        resolved = True
                        break

            if finding.status == FindingStatus.REMEDIATED:
                result.resolved_findings.append(finding)
            elif finding.status == FindingStatus.WAIVED:
                result.waived_findings.append(finding)
            elif attempt_fn is None:
                # Classification-only mode: findings are classified but not remediated
                result.open_findings.append(finding)
                if finding.is_blocking or finding.requires_human_waiver:
                    result.all_resolved = False
            elif not resolved:
                # Escalate non-converging findings
                if finding.is_blocking or finding.requires_human_waiver:
                    finding.status = FindingStatus.MANUAL_REQUIRED
                    result.escalated_findings.append(finding)
                    result.requires_manual_intervention = True
                    result.status = FindingStatus.MANUAL_REQUIRED.value
                    result.all_resolved = False
                else:
                    finding.status = FindingStatus.ESCALATED
                    result.escalated_findings.append(finding)
                    result.all_resolved = False
            else:
                result.open_findings.append(finding)

        if result.requires_manual_intervention:
            manual_ids = ", ".join(
                f.finding_id
                for f in result.escalated_findings
                if f.status == FindingStatus.MANUAL_REQUIRED
            )
            result.status = FindingStatus.MANUAL_REQUIRED.value
            result.exhausted_error = RemediationExhaustedError(
                f"Automatic remediation exhausted for findings: {manual_ids}",
                result=result,
            )
            raise result.exhausted_error
        return result

    def waive(self, finding: Finding, approver: str) -> bool:
        """Waive a finding.  Security critical/high require an explicit approver."""
        if finding.requires_human_waiver and not approver:
            return False
        if finding.requires_human_waiver:
            finding.status = FindingStatus.WAIVED
            finding.remediation_guidance += f"\n[WAIVED by {approver}]"
            return True
        if not finding.waiver_eligible:
            return False
        finding.status = FindingStatus.WAIVED
        return True

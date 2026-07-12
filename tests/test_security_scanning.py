"""Tests for TASK-055: Security Scanning."""

from __future__ import annotations

from validators.security_scanner import SecurityScanner, Severity
from validators.remediation import (
    BoundedRemediationLoop,
    Finding,
    FindingCategory,
    FindingSeverity,
    FindingStatus,
)


def test_hardcoded_password_detected() -> None:
    scanner = SecurityScanner()
    result = scanner.scan('test_artifact', 'password = "hunter2"')
    assert not result.passed
    findings = [f for f in result.findings if f.rule_id == 'SEC001']
    assert len(findings) >= 1


def test_hardcoded_api_key_detected() -> None:
    scanner = SecurityScanner()
    result = scanner.scan('artifact', 'api_key = "sk-abcdefghijklmnop"')
    assert any(f.rule_id == 'SEC002' for f in result.findings)


def test_eval_detected() -> None:
    scanner = SecurityScanner()
    result = scanner.scan('code', 'result = eval(user_input)')
    assert any(f.rule_id == 'SEC005' for f in result.findings)


def test_clean_content_passes() -> None:
    scanner = SecurityScanner()
    result = scanner.scan('clean', '# This is fine\nprint("hello")\n')
    assert result.passed
    assert result.finding_count == 0


def test_passed_property_ignores_low_severity() -> None:
    scanner = SecurityScanner()
    result = scanner.scan('code', '# TODO: review auth token handling')
    # INFO finding only — should still pass
    assert result.passed


def test_scan_many() -> None:
    scanner = SecurityScanner()
    artifacts = {
        'clean': '# OK code',
        'bad': 'password = "secret123"',
    }
    results = scanner.scan_many(artifacts)
    assert len(results) == 2
    clean = next(r for r in results if r.artifact_name == 'clean')
    bad = next(r for r in results if r.artifact_name == 'bad')
    assert clean.passed
    assert not bad.passed


def test_finding_line_number() -> None:
    scanner = SecurityScanner()
    content = 'import os\npassword = "abc123xyz"\nprint("done")'
    result = scanner.scan('code', content)
    pwd_findings = [f for f in result.findings if f.rule_id == 'SEC001']
    assert pwd_findings[0].line_number == 2


def test_critical_security_cannot_be_auto_waived() -> None:
    scanner = SecurityScanner()
    result = scanner.scan('code', 'password = "abc123xyz"\n')
    critical = next(f for f in result.findings if f.severity == Severity.CRITICAL)
    loop = BoundedRemediationLoop()
    finding = Finding(
        finding_id='sec-1',
        severity=FindingSeverity(critical.severity.value),
        category=FindingCategory.SECURITY,
        message=critical.message,
        waiver_eligible=True,
    )

    waived = loop.waive(finding, approver='')

    assert waived is False
    assert finding.status == FindingStatus.OPEN

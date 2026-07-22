"""Deterministic helpers for the Slugger issue-to-Codex bridge."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

SOURCE_MARKER_RE = re.compile(
    r"<!--\s*portfolio-task-source:\s*Young-Consultations/portfolio-tasks#(?P<number>[1-9][0-9]{0,8})\s*-->"
)
OLD_SOURCE_MARKER_RE = re.compile(
    r"<!--\s*(?:chatgpt-task-source|slugger-task-source):", re.I
)
FIELD_RE = re.compile(
    r"<!--\s*slugger-field:\s*(?P<name>[a-z_]+)\s*-->(?P<value>.*?)<!--\s*/slugger-field:\s*(?P=name)\s*-->",
    re.S,
)
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REQUIRED_FIELDS = ("idea", "project_name", "target_repository")
MAX_FIELD_LENGTHS = {"idea": 8000, "project_name": 80, "target_repository": 120}
PROMPT_VERSION = "issue-to-codex-v1"


class IssueBridgeError(ValueError):
    """Raised when untrusted issue content fails closed validation."""


@dataclass(frozen=True)
class IssueContract:
    source_issue_number: int
    source_issue_url: str
    portfolio_task_number: int
    idea: str
    project_name: str
    target_repository: str
    request_identity: str


def load_allowlist(path: str | Path) -> set[str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    repos = data.get("allowed_target_repositories")
    if not isinstance(repos, list) or not repos:
        raise IssueBridgeError("target repository allowlist is missing")
    result = set()
    for repo in repos:
        if not isinstance(repo, str) or not REPO_RE.fullmatch(repo):
            raise IssueBridgeError(
                "target repository allowlist contains an invalid entry"
            )
        result.add(repo)
    return result


def _extract_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    seen: set[str] = set()
    for match in FIELD_RE.finditer(body):
        name = match.group("name")
        if name in seen:
            raise IssueBridgeError(f"duplicate required field: {name}")
        seen.add(name)
        fields[name] = match.group("value").strip()
    for name in REQUIRED_FIELDS:
        if name not in fields or not fields[name]:
            raise IssueBridgeError(f"missing required field: {name}")
        if len(fields[name]) > MAX_FIELD_LENGTHS[name]:
            raise IssueBridgeError(f"field exceeds maximum length: {name}")
    return fields


def parse_issue_contract(
    *,
    body: str,
    issue_number: int,
    issue_url: str,
    allowlist: set[str],
) -> IssueContract:
    if len(body) > 20000:
        raise IssueBridgeError("issue body exceeds maximum length")
    if OLD_SOURCE_MARKER_RE.search(body):
        raise IssueBridgeError("unsupported legacy source marker")
    source = SOURCE_MARKER_RE.search(body)
    if source is None:
        raise IssueBridgeError("missing portfolio task source marker")
    if len(SOURCE_MARKER_RE.findall(body)) != 1:
        raise IssueBridgeError("duplicate portfolio task source marker")
    fields = _extract_fields(body)
    target_repository = fields["target_repository"]
    if not REPO_RE.fullmatch(target_repository):
        raise IssueBridgeError("target repository must use owner/repository format")
    if target_repository not in allowlist:
        raise IssueBridgeError("target repository is not allowlisted")
    normalized = {
        "source_issue_number": issue_number,
        "target_repository": target_repository,
        "project_name": fields["project_name"],
        "idea_sha256": hashlib.sha256(fields["idea"].encode("utf-8")).hexdigest(),
        "prompt_version": PROMPT_VERSION,
    }
    request_identity = hashlib.sha256(
        json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return IssueContract(
        source_issue_number=issue_number,
        source_issue_url=issue_url,
        portfolio_task_number=int(source.group("number")),
        idea=fields["idea"],
        project_name=fields["project_name"],
        target_repository=target_repository,
        request_identity=request_identity,
    )


def actor_is_authorized(actor: str, authorized_actors: str) -> bool:
    allowed = {
        item.strip().lower() for item in authorized_actors.split(",") if item.strip()
    }
    return bool(actor) and actor.lower() in allowed


def write_github_outputs(contract: IssueContract, output_path: str | Path) -> None:
    with Path(output_path).open("a", encoding="utf-8") as out:
        for key in (
            "idea",
            "project_name",
            "target_repository",
            "source_issue_number",
            "source_issue_url",
            "request_identity",
        ):
            value = str(getattr(contract, key))
            delimiter = f"SLUGGER_{key.upper()}_EOF"
            out.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")


def main() -> None:
    allowlist = load_allowlist(os.environ["SLUGGER_TARGET_ALLOWLIST"])
    contract = parse_issue_contract(
        body=Path(os.environ["ISSUE_BODY_FILE"]).read_text(encoding="utf-8"),
        issue_number=int(os.environ["ISSUE_NUMBER"]),
        issue_url=os.environ["ISSUE_URL"],
        allowlist=allowlist,
    )
    write_github_outputs(contract, os.environ["GITHUB_OUTPUT"])


if __name__ == "__main__":
    main()

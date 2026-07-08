<!--
  templates/Requirements.md
  Purpose: Generic, testable functional and non-functional requirements template.
  Use this template to capture requirements in a format suitable for traceability and test planning.
-->

# Requirements

Project: [PROJECT_NAME]
Version: [VERSION]
Last updated: [DATE]

## Usage guidance
- Keep requirements atomic and testable.
- Assign unique IDs (REQ-001, NFR-001) for traceability.
- Include acceptance criteria that can be automated where possible.

---

## Functional requirements

- ID: REQ-001
  Title: [Short title]
  Description: [Clear, unambiguous description of expected behavior]
  Rationale: [Why this is needed]
  Acceptance criteria:
    - Given [preconditions], when [action], then [observable result]
  Priority: [P0/P1/P2]
  Trace: [Design docs / ADR / TestCase]

- ID: REQ-002
  Title: ...

(Continue listing functional requirements)

---

## Non-functional requirements

- ID: NFR-001
  Title: Performance
  Description: [e.g., "99th percentile response time < 200ms for endpoint X under Y load"]
  Acceptance criteria:
    - [Concrete measurable targets]
  Priority: [P0/P1]

- ID: NFR-002
  Title: Security
  Description: [e.g., "Secrets must be stored in a secret manager; no plaintext in repo"]
  Acceptance criteria:
    - [E.g., "No plaintext secrets found by scanner in repo"]

(Continue: scalability, reliability, maintainability, observability, compliance)

---

## Dependencies
- [External services, libraries, or systems required]

## Open questions & risks
- Q1: [Open question impacting requirement]
- R1: [Risk description and mitigation]

## Traceability matrix
- Map requirement IDs to ADRs, design docs, test cases, and tickets.


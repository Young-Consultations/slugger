<!--
  templates/RiskRegister.md
  Purpose: Generic risk register template to track project risks, owners, mitigations, and status.
  Instructions: Copy one risk row per risk and keep this file reviewed regularly.
-->

# Risk Register

Project: [PROJECT_NAME]
Last updated: [YYYY-MM-DD]

> Summary: Use this register to identify, assess, track, and mitigate risks throughout the project lifecycle.

## How to use
- Add each risk as a separate entry with a unique ID (e.g., R-001).
- Update Likelihood and Impact as more information becomes available.
- Owner is responsible for tracking mitigation and updating status.

## Risk table (summary)
| ID | Risk description | Likelihood (L/M/H) | Impact (L/M/H) | Score (LxI) | Owner | Mitigation / Action | Status | Review date |
|----|------------------|--------------------:|----------------:|------------:|-------|---------------------|--------|-------------|
| R-001 | Example: Third-party API rate limits affect critical flows | M | H | MxH | @team | Implement retries, exponential backoff, and circuit breaker. Add caching. | Open | [YYYY-MM-DD] |


## Risk details (template per risk)

### R-XXX: [Short title]
- ID: R-XXX
- Description: [Detailed description of the risk, why it matters]
- Trigger/Indicators: [Signals that the risk may be occurring]
- Likelihood: [Low / Medium / High]
- Impact: [Low / Medium / High]
- Score: [Guidance: map LxI to a relative priority (e.g., HxH = Critical)]
- Owner: [Name or role responsible]
- Mitigation actions:
  - Action 1: [What will be done to reduce likelihood]
  - Action 2: [What will be done to reduce impact]
- Contingency plan:
  - [What to do if the risk materializes despite mitigations]
- Dependencies: [Related requirements, ADRs, or external systems]
- Status: [Open / Monitoring / Mitigated / Closed]
- Last updated: [YYYY-MM-DD]

## Risk assessment methodology
- Likelihood: qualitative estimate based on evidence (Low/Medium/High).
- Impact: qualitative estimate based on business/technical consequences.
- Score: combine Likelihood and Impact to prioritize (e.g., use a 3x3 matrix).

### Example scoring matrix
- Low x Low = Low priority
- Low x High = Medium priority
- High x High = Critical priority

## Review cadence
- High and critical risks: review weekly.
- Medium risks: review bi-weekly.
- Low risks: review monthly or on milestone boundaries.

## Reporting & escalation
- Owners update the register during standups or risk review meetings.
- Critical issues escalate to Product and Engineering leadership and are tracked as action items.

## Links / Traceability
- Related requirements: [REQ-xxx]
- Related ADRs: [docs/adr/NNNN-*.md]
- Related tests: [tests/test_*.py or QA plan sections]

## Archive / Closure notes
- When a risk is closed, record the reason and the evidence that shows it is mitigated.
- Move closed risks to an archive section with date closed and summary of resolution.


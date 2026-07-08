<!--
  templates/SecurityReviews.md
  Purpose: Security review checklist and template for documenting security considerations and findings.
-->

# Security Review Template

Project: [PROJECT_NAME]
Review date: [YYYY-MM-DD]
Reviewer(s): [Name(s) / role(s)]

## Scope
- Components/services in scope: [list]
- Out-of-scope: [list]

## Assets & Threat Model Summary
- Critical assets: [credentials, customer data, keys]
- High-level threat model: [brief description of threat flows, trust boundaries]

## Checklist (Initial review)
- Authentication & Authorization
  - [ ] Strong authentication enforced (e.g., OAuth2, JWT, SAML) where required
  - [ ] Principle of least privilege for service accounts and roles
- Secrets Management
  - [ ] No plaintext secrets in source control
  - [ ] Use secret manager (e.g., AWS Secrets Manager, Vault)
- Data Protection
  - [ ] Sensitive data is encrypted at rest and in transit
  - [ ] Data retention and deletion policies documented
- Input Validation & Output Encoding
  - [ ] Validate and sanitize inputs from untrusted sources
  - [ ] Protect against injection (SQL, command, template) and XSS
- Dependency & Supply Chain
  - [ ] Dependency scanning enabled and configured
  - [ ] Pin or lock dependency versions for reproducible builds
- Infrastructure & Network Security
  - [ ] Use private subnets for sensitive services
  - [ ] Minimal open network ports; firewall rules reviewed
- Logging & Monitoring
  - [ ] Sensitive data redaction in logs
  - [ ] Alerts configured for suspect behavior
- CI/CD Security
  - [ ] Secrets not exposed in CI logs
  - [ ] Signed build artifacts where appropriate
- Secure Defaults
  - [ ] Secure configurations by default; opt-in for weaker security

## Findings & Recommendations
- Finding 1: [Title]
  - Severity: [Low/Medium/High/Critical]
  - Description: [What was found and evidence]
  - Recommendation: [Action to remediate]
  - Owner: [Name/Role]
  - Target date: [YYYY-MM-DD]

- Finding 2: ...

## Risk Assessment
- Summarize residual risks after remediation and the acceptance of those risks.

## Approval
- Security reviewer: [name signature / approval]
- Product owner: [name signature / approval]

## Follow-up & Verification
- Re-check schedule: [date or condition for re-review]
- Verification steps to confirm remediation: [tests, scans, or manual verification]

## References
- Internal policies, compliance standards (e.g., SOC2, GDPR), and relevant ADRs.


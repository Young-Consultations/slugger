<!--
  templates/DeploymentGuides.md
  Purpose: Generic deployment guide template covering build, deploy, rollback, and runbook procedures.
-->

# Deployment Guide

Project: [PROJECT_NAME]
Environment: [staging/production]
Last updated: [YYYY-MM-DD]

## Overview
Describe the deployment model (containers, serverless, VMs) and key components. Include links to infra-as-code.

## Pre-deployment checks
- All tests pass in CI (unit/integration/regression).
- Release artifact created and stored (image tag, artifact ID).
- Database migrations reviewed and backward-compatible where possible.
- Monitoring and alerting configured for new release.

## Deployment steps (example for containerized app)
1. Build:
   - Build and tag Docker image: `docker build -t registry/project:TAG .`
   - Push to registry: `docker push registry/project:TAG`
2. Deploy:
   - Update deployment manifests (k8s) with new image tag.
   - Apply manifests: `kubectl apply -f manifests/` or use helm: `helm upgrade --install`
3. Migrations:
   - Run DB migrations in a safe order; prefer non-blocking background migrations.
4. Smoke tests:
   - Run basic health checks and smoke tests against new instances.
5. Promote traffic:
   - Shift traffic gradually if supported (canary/blue-green) and monitor metrics and logs.

## Rollback procedure
- If critical errors are detected, rollback to the previous image/tag immediately:
  - `helm rollback <release> <previous_revision>` or `kubectl rollout undo deployment/<name>`
- If database migrations are destructive, follow contingency plan and coordinate with engineering/product for manual remediation.

## Runbook & Troubleshooting
- Common issues and remediation steps
  - Service fails health check: check logs, container events, and dependency services
  - Increased error rate: rollback and inspect recent changes in code and infra
  - DB migration failure: stop deployment, restore DB snapshot if required

## Post-deployment validation
- Verify key health endpoints, metrics, and logs.
- Confirm downstream systems are functioning.
- Notify stakeholders and update release notes.

## Access & Permissions
- List who can deploy and emergency contacts.
- Document escalation paths for incidents.

## Automation & CI/CD
- Describe CI workflows that build and deploy artifacts (GitHub Actions, CircleCI, etc.).
- Provide links to pipeline definitions and secrets management documentation.

## Security & Compliance
- Ensure that secrets are not hardcoded into manifests.
- Access to deployment tooling should be audited.

## Maintenance
- Update this guide when deployment topology or processes change.
- Periodically rehearse rollback and disaster recovery procedures.


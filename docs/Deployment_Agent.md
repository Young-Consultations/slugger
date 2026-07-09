# Deployment Agent

This document describes the Deployment agent in the orchestrator pipeline.

## Deployment Agent

**Purpose**: Generate comprehensive deployment configurations, CI/CD workflows, and infrastructure-as-code for cloud deployment.

**Input**:
- `artifact` (dict, optional): The documentation artifact from a prior step.
- `code_text` (str, optional): Raw code scaffold text.
- `documentation_text` (str, optional): Raw documentation text.
- `_provider` (AIProvider): Injected by the Orchestrator.

**Output**:
- `artifact` (dict): Contains `type: "deployment_config"` and the generated configurations.
- `artifact_name` (str): "deployment_config_v1"
- `status` (str): "success" or "error"

## Generated Deployment Configurations

The Deployment agent generates comprehensive deployment infrastructure including:

1. **GitHub Actions Workflows** — Continuous integration and deployment
   - CI workflow: build, lint, test, coverage
   - CD workflow: deploy to staging and production
   - Pre-commit hooks workflow
   - Release workflow: version bumping, changelog
   - Schedule workflows: security scans, dependency updates

2. **Docker Configuration** — Containerization
   - Dockerfile (multi-stage build)
   - .dockerignore file
   - Docker Compose for local development
   - Docker Compose for production
   - Container health checks
   - Security scanning configuration

3. **Kubernetes Manifests** — Cloud-native deployment
   - Deployment YAML
   - Service YAML
   - Ingress YAML
   - ConfigMap and Secret templates
   - HorizontalPodAutoscaler YAML
   - NetworkPolicy YAML
   - RBAC configurations

4. **Infrastructure-as-Code** — Cloud provisioning
   - Terraform modules (AWS, GCP, Azure)
   - CloudFormation templates
   - Bicep templates (Azure)
   - VPC, security groups, load balancers
   - Database provisioning
   - CDN and caching configuration

5. **Deployment Scripts** — Automation
   - Bash scripts for deployments
   - Python scripts for infrastructure setup
   - Database migration scripts
   - Rollback procedures
   - Health check scripts

6. **Environment Configuration** — Multi-environment setup
   - .env.example template
   - Development environment config
   - Staging environment config
   - Production environment config
   - Secret management integration

7. **Monitoring and Logging** — Observability
   - Prometheus metrics configuration
   - Grafana dashboards
   - ELK Stack setup
   - CloudWatch configuration (AWS)
   - Datadog integration
   - Alert rules and thresholds

8. **Security Configurations** — Security hardening
   - SSL/TLS certificate management
   - Web Application Firewall (WAF) rules
   - Network security policies
   - Secret rotation procedures
   - Security scanning configurations
   - DDoS protection setup

9. **Load Balancing and Scaling** — Performance
   - Load balancer configuration
   - Auto-scaling policies
   - Cache invalidation strategies
   - Database connection pooling
   - Rate limiting configuration

10. **Backup and Disaster Recovery** — Business continuity
    - Backup automation scripts
    - Disaster recovery playbooks
    - RTO/RPO targets
    - Test restoration procedures
    - Cross-region replication setup

## Full Pipeline Example

The Deployment agent extends the orchestration pipeline to include comprehensive deployment infrastructure:

```python
from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.agents import (
    RequirementsAgent, BusinessAnalystAgent, ArchitectureAgent,
    PlanningAgent, CodingAgent, TestingAgent, DocumentationAgent,
    DeploymentAgent
)

orch = Orchestrator()
for agent_class in [RequirementsAgent, BusinessAnalystAgent, ArchitectureAgent,
                    PlanningAgent, CodingAgent, TestingAgent, DocumentationAgent,
                    DeploymentAgent]:
    orch.register_agent(agent_class())

result = orch.run_pipeline(
    ["requirements", "business_analyst", "architecture", "planning", 
     "coding", "testing", "documentation", "deployment"],
    context={"request": "Build a collaborative document editor"},
)
print(result["artifact"]["content"])  # Deployment configurations
```

## Agent Chaining

The Deployment agent receives all prior outputs and generates deployment infrastructure:

1. **Requirements Agent** generates requirements document
2. **Business Analyst Agent** generates user stories and analysis
3. **Architecture Agent** generates system design
4. **Planning Agent** generates project plan
5. **Coding Agent** generates code scaffolds
6. **Testing Agent** generates test scaffolds
7. **Documentation Agent** generates comprehensive documentation
8. **Deployment Agent** generates deployment configurations and CI/CD workflows

## Generated Deployment Structure

Example deployment structure:

```
.github/
  workflows/
    ci.yml
    cd.yml
    release.yml
    security-scan.yml

docker/
  Dockerfile
  .dockerignore
  docker-compose.yml
  docker-compose.prod.yml

infrastructure/
  terraform/
    aws/
      main.tf
      variables.tf
      outputs.tf
    gcp/
    azure/
  kubernetes/
    deployment.yaml
    service.yaml
    ingress.yaml
    configmap.yaml
  cloudformation/
    template.yaml

scripts/
  deploy.sh
  rollback.sh
  health-check.sh
  migrate-db.sh

monitoring/
  prometheus.yml
  grafana-dashboards/
  elk-stack/
  datadog-config.yaml

.env.example
.env.development
.env.staging
.env.production
```

Each configuration file includes:
- Complete, production-ready configuration
- Comments explaining each section
- Security hardening best practices
- Troubleshooting guides
- Links to official documentation

"""Deployment agent.

This agent accepts code, tests, and documentation, and generates
CI/CD workflows, deployment scripts, and infrastructure-as-code configurations.
"""
from typing import Any, Dict

from slugger.orchestrator.agents.base import Agent


class DeploymentAgent(Agent):
    name = "deployment"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment configurations and CI/CD workflows.

        Expects inputs:
        - artifact: (optional) The documentation artifact from a prior step
        - code_text: (optional) Raw code scaffold text
        - documentation_text: (optional) Raw documentation text
        - _provider: (injected by Orchestrator) The AI provider

        Returns:
        - artifact: The deployment and CI/CD configurations
        - artifact_name: A name for the artifact
        - status: 'success' or 'error'
        """
        provider = inputs.get("_provider")

        # Extract context from artifact or raw text
        context_text = ""
        if "artifact" in inputs and isinstance(inputs["artifact"], dict):
            context_text = inputs["artifact"].get("content", "")
        if not context_text:
            context_text = inputs.get("code_text", "")
        if not context_text:
            context_text = inputs.get("documentation_text", "")

        if not context_text:
            return {"status": "error", "message": "No code, documentation, or deployment context provided"}
        if not provider:
            return {"status": "error", "message": "No provider available"}

        prompt = f"""You are a DevOps engineer and infrastructure expert. Based on the following code, tests,
and documentation, generate comprehensive deployment configurations and CI/CD workflows including:

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
   - ELK Stack (Elasticsearch, Logstash, Kibana) setup
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

For each configuration, provide:
- File path and name
- Complete configuration content
- Comments explaining key sections
- Best practices and security hardening tips
- Troubleshooting guides

Code, Tests & Documentation:
{context_text}

Generate comprehensive deployment configurations:"""

        result = provider.generate(prompt)
        deployment_config = result.get("response", "")

        return {
            "artifact": {
                "type": "deployment_config",
                "content": deployment_config,
            },
            "artifact_name": "deployment_config_v1",
            "status": "success",
        }

# Security Engineer Agent

## Overview

The Security Engineer Agent is responsible for protecting systems and data through security architecture, vulnerability assessment, and security controls implementation. This agent ensures that security is built into systems from the ground up and maintains defenses against evolving threats.

## Responsibilities

### Primary Responsibilities

- **Security Architecture**: Design security controls and threat mitigation strategies
- **Threat Analysis**: Identify and assess security threats and risks
- **Vulnerability Assessment**: Identify security vulnerabilities in systems and code
- **Security Reviews**: Conduct security reviews of designs, code, and configurations
- **Access Control**: Design and implement authentication and authorization mechanisms
- **Data Protection**: Ensure data is encrypted, protected, and handled securely
- **Incident Response**: Respond to security incidents and investigate breaches
- **Compliance**: Ensure compliance with security regulations and standards
- **Security Testing**: Conduct penetration testing and security assessments

## Inputs

### Required Inputs

| Input | Source | Format | Description |
|-------|--------|--------|-------------|
| System Architecture | Solution Architect | Architecture docs | System design and components |
| Regulatory Requirements | Legal/Compliance | Compliance docs | Security and compliance requirements |
| Security Policies | Security/Compliance | Policy documents | Organization security policies |
| Data Classification | Data Governance | Classification matrix | How data should be protected |
| Threat Intelligence | Security Team | Reports | Known threats and vulnerabilities |
| User Stories & Features | Product Owner | Requirements | Features to assess for security |

## Outputs

### Primary Outputs

| Output | Consumer | Format | Description |
|--------|----------|--------|-------------|
| Security Architecture | Architect/Dev Team | Design document | Security controls and implementation approach |
| Threat Model | Architecture/Team | Document, Diagrams | Identified threats and mitigation strategies |
| Vulnerability Report | Development Team | Report | Identified vulnerabilities and fixes |
| Security Review | Team/Management | Review document | Security assessment and recommendations |
| Penetration Test Report | Management/DevOps | Report | Penetration testing results and findings |
| Access Control Design | Infrastructure/Dev | Specification | Authentication/authorization implementation |
| Security Incident Report | Management | Report | Incident analysis and recommendations |

## Acceptance Criteria

### Definition of Done for Security Engineer Work

- [ ] All system components reviewed for security
- [ ] Threat model created with identified threats
- [ ] Mitigation strategies documented
- [ ] Security controls specified and prioritized
- [ ] Risk levels assigned to threats
- [ ] Compliance requirements addressed
- [ ] Architecture reviewed by security team
- [ ] Recommendations documented
- [ ] Code reviewed for vulnerabilities
- [ ] Penetration testing completed (if applicable)

## OWASP Top 10 Checklist

Verify protection against top vulnerabilities:

- [ ] Broken Access Control
- [ ] Cryptographic Failures
- [ ] Injection
- [ ] Insecure Design
- [ ] Security Misconfiguration
- [ ] Vulnerable Components
- [ ] Authentication Failures
- [ ] Software and Data Integrity Failures
- [ ] Logging and Monitoring Failures
- [ ] SSRF

## Related Agents

- **Solution Architect**: Provides technical design
- **Backend Engineer**: Implements security controls
- **Frontend Engineer**: Implements client-side security
- **DevOps Engineer**: Implements infrastructure security
- **Product Owner**: Provides security requirements

## Revision History

| Version | Date | Changes |
|---------|------|----------|
| 1.0 | [DATE] | Initial template creation |

---

*This is a generic template. Customize with your specific security standards.*
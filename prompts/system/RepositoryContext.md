# Slugger Repository Context
Version: 1.0.0

---

# Purpose

This document defines the structure, standards, conventions, architecture, and operational expectations for the Slugger repository.

Every AI agent working within this repository should treat this document as the primary reference for understanding how the project is organized and how changes should be made.

If this document conflicts with a task prompt, ask for clarification or preserve the documented architecture rather than making assumptions.

---

# Project Identity

Project Name:

Slugger

Project Type:

AI Software Factory

Primary Language:

Python

Primary Mission:

Transform software ideas into production-ready software systems by orchestrating specialized AI agents that execute the complete Software Development Life Cycle (SDLC).

Slugger should produce not only source code but also the complete set of engineering artifacts expected from a mature software organization.

The Slugger repository is itself the first project managed by Slugger and should exemplify the engineering standards it promotes.

---

# Naming Philosophy

The name "Slugger" comes from baseball.

A slugger is the player every team wants because they consistently hit home runs.

Likewise, Slugger is intended to be the AI "free agent" that software organizations want on their team—an autonomous engineering platform that takes an idea and "knocks it out of the park" by delivering high-quality software and the complete engineering process behind it.

This metaphor should influence documentation, messaging, and examples without becoming overly repetitive.

---

# Guiding Principles

Always favor:

Maintainability

Extensibility

Automation

Traceability

Testability

Readability

Consistency

Modularity

Documentation

Long-term sustainability

Avoid short-term optimizations that create future technical debt.

---

# Repository Organization

The repository is organized around distinct responsibilities.

Typical top-level directories include:

- agents/
- artifacts/
- config/
- core/
- docs/
- examples/
- knowledge/
- logs/
- memory/
- metrics/
- models/
- observability/
- orchestrator/
- plugins/
- prompts/
- providers/
- scripts/
- services/
- state_machine/
- templates/
- tests/
- validators/
- workflow/

Each directory has a single, well-defined purpose and should contain its own README describing its contents and responsibilities.

---

# Documentation Hierarchy

Documentation is a first-class deliverable.

The `docs/` directory should contain:

- Vision
- Roadmap
- AI-SDLC Specification
- Architecture
- Domain Model
- Workflow DSL
- Coding Standards
- Design Principles
- Security Architecture
- Quality Standards
- Testing Strategy
- Deployment Strategy
- Agent Specification
- Architecture Decision Records (ADRs)

All significant architectural decisions should be recorded as ADRs.

---

# Knowledge System

The knowledge directory represents long-term organizational memory.

It should include areas such as:

- Engineering references
- Prompt engineering
- Software architecture
- Python development
- iOS development
- GitHub automation
- Design patterns
- Security
- Testing
- Deployment
- Lessons learned
- Reusable examples
- Decisions

Knowledge should be reusable across projects and continuously improved.

---

# Prompt Library

Prompts are version-controlled engineering assets.

The prompt hierarchy should distinguish between:

- System prompts
- Task prompts
- Prompt templates
- Prompt examples

The `prompts/system/` directory contains the permanent operating guidance for AI agents.

The `templates/` directory contains reusable document templates.

Prompt changes should be documented and reviewed like code changes.

---

# Plugin Architecture

Slugger is designed to be extensible.

Major capabilities should be implemented as plugins whenever practical.

Plugins may include:

- AI providers
- Agents
- Workflows
- Validators
- Artifact generators
- Integrations

The orchestrator should discover plugins dynamically rather than relying on hardcoded registrations.

---

# Agent Architecture

Each agent should:

Have one primary responsibility.

Declare its capabilities.

Declare dependencies.

Define expected inputs.

Define expected outputs.

Expose metadata.

Support validation.

Avoid direct dependencies on other agents whenever possible.

Communication should occur through shared artifacts and workflows.

---

# Workflow Architecture

Workflows should be declarative whenever practical.

Prefer YAML definitions over hardcoded logic.

Each workflow should define:

Purpose

Inputs

Outputs

Dependencies

Quality gates

Recovery behavior

Approval requirements

Execution should remain observable and restartable.

---

# Artifact Management

Artifacts are first-class outputs.

Artifacts include, but are not limited to:

Requirements

User Stories

Architecture

UML

Source Code

Tests

Documentation

Deployment Packages

Release Notes

Risk Registers

Decision Logs

Every artifact should have traceability to its originating requirements and workflow.

---

# Coding Standards

Follow:

PEP 8

Type hints

Meaningful naming

Small functions

Single responsibility

Dependency injection

Composition over inheritance

Clear interfaces

Consistent formatting

Avoid premature optimization.

---

# Testing Standards

New behavior should include appropriate automated tests.

Testing should emphasize:

Unit testing

Integration testing

Validation testing

Regression testing when appropriate

Tests should verify observable behavior rather than implementation details.

---

# Documentation Standards

Documentation should evolve alongside implementation.

Update documentation whenever:

Architecture changes

Interfaces change

Behavior changes

Configuration changes

Workflows change

Knowledge improves

Documentation should never become stale intentionally.

---

# Git Standards

Favor:

Small commits

Focused commits

Meaningful commit messages

Atomic changes

Feature branches

Code review

Avoid mixing unrelated work in a single commit.

---

# Configuration Standards

Prefer external configuration.

Avoid hardcoded values.

Support environment-specific configuration.

Configuration should be version-controlled where appropriate.

Secrets should never be committed.

---

# Error Handling

Fail predictably.

Provide actionable error messages.

Log sufficient diagnostic information.

Support retries where appropriate.

Favor graceful degradation over unexpected failures.

---

# Observability

Capture:

Execution metrics

Workflow state

Prompt usage

Agent activity

Token usage

Estimated AI costs

Performance

Warnings

Errors

Observability is a required capability, not an optional enhancement.

---

# Quality Gates

Each significant phase should define:

Required inputs

Expected outputs

Validation rules

Completion criteria

Approval requirements

Do not advance a workflow until quality gates are satisfied.

---

# Repository Evolution

This repository is expected to evolve continuously.

Favor designs that:

Support future AI models

Support additional programming languages

Support new workflow types

Support new artifact generators

Support new deployment targets

Support future plugin types

Avoid architecture that limits future growth.

---

# Definition of Done

A task is complete only when:

Architecture remains consistent.

Code follows project standards.

Documentation is updated.

Tests are added or updated when appropriate.

Quality gates are satisfied.

No unnecessary technical debt is introduced.

The repository is in a better state than before the task began.

---

# Standard Operating Procedure

Before modifying the repository:

1. Read `MasterOrchestrator.md`.
2. Read `MasterMarketSimulation.md`.
3. Read this document.
4. Review Architecture Decision Records.
5. Inspect the existing implementation.
6. Identify reusable components.
7. Produce an implementation plan.
8. Explain the plan.
9. Implement incrementally.
10. Validate the results.
11. Update documentation.
12. Update tests.
13. Prepare a focused commit.
14. Summarize completed work.

Never bypass these steps without explicit instruction.

---

# Final Principle

Treat the Slugger repository as a living example of elite software engineering.

Every commit, document, prompt, workflow, template, test, and architectural decision should demonstrate the quality, discipline, and repeatability that Slugger is designed to deliver for future software projects.

Build the repository today as if it will become the reference implementation that future AI software factories will study and emulate.
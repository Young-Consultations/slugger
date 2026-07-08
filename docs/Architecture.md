<!--
  docs/Architecture.md
  Purpose: architecture overview, components, data flow, and deployment guidance.
  Keep this file high-level and link to component-level docs when they exist.
-->

# Architecture

## Overview
Slugger is a modular service that transforms arbitrary strings into stable, URL-safe slugs and exposes generation and validation interfaces.
The design favors stateless, horizontally-scalable API instances with optional persistence for canonical slug mappings.

## High-level components
- API Layer
  - HTTP server exposing REST endpoints (generate, validate, batch).
  - Authentication and authorization middleware.
- Core Slug Engine
  - Normalization: Unicode normalization (NFKC/NFKD), trimming, case folding.
  - Transliteration: optional, configurable transliteration for non-Latin scripts.
  - Tokenization & filtering: remove stopwords, punctuation, and control maximum token length.
  - Formatting: join tokens using configured separators ("-" by default) and enforce length limits.
- Collision Manager
  - Strategy interface for deterministic suffixing or datastore-backed uniqueness checks.
- Persistence (optional)
  - Store canonical mapping input -> slug when required; keep persistence pluggable (in-memory, SQL, NoSQL).
- Workers / Batch Processor
  - Process large jobs asynchronously, with retries and idempotency guarantees.
- Observability
  - Metrics (Prometheus-style), structured logs, and tracing hooks.

## Data flow
1. Client -> API (POST /v1/slugs)
2. API validates payload and auth, applies input constraints
3. API invokes Core Slug Engine with configured pipeline
4. Engine returns slug(s); collision manager may be invoked
5. API optionally persists mapping and returns response

Client -> API -> Core Engine -> (Collision Manager -> Persistence)
                       \-> Observability

## Deployment
- Containerized application (Docker).
- Deploy via Kubernetes/Helm or simple container hosts.
- Health and readiness endpoints: `/healthz`, `/readyz`, `/metrics`.
- Use rolling updates with readiness checks for zero-downtime deploys.

## Scalability & Reliability
- Keep Core Engine stateless; persist only when canonical mappings are required.
- Autoscale API replicas on CPU/latency/queue metrics.
- Use circuit breakers and retries with exponential backoff for external dependencies.

## Security
- Enforce TLS for all external traffic.
- Require authentication for write operations; implement rate limiting.
- Validate payload sizes to mitigate OOM/DoS.

## Key design decisions
- Determinism by default to ensure same input -> same slug.
- Separate normalization, transliteration, and formatting to make the pipeline configurable and testable.
- Pluggable persistence layer to allow in-memory mode for simple deployments and durable stores for production.

## Extensibility
- Expose configuration for stopword lists, transliteration rules, and formatting policies.
- Provide SDKs or client libraries in consumer languages when needed.

## Operational considerations
- Backups for persistent stores and migration plans for slug reformatting.
- Monitoring dashboards for request rates, error rates, and collision frequency.


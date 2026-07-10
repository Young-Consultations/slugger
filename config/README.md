# config/

This directory contains all configuration files for the Slugger system.

## Purpose

Centralize environment-specific and system-wide configuration so that behavior is controlled through external settings rather than hardcoded values.

## Conventions

- Prefer YAML or TOML for configuration files.
- Support multiple environments (development, test, production) via separate files or environment variables.
- Secrets must never be committed to this directory; use environment variables or a secrets manager.
- Default configuration values should be safe and conservative.

## Typical Contents

- `default.yaml` — baseline configuration applied across all environments
- `development.yaml` — overrides for local development
- `production.yaml` — overrides for production deployments
- `logging.yaml` — logging configuration
- `providers.yaml` — AI provider configuration

## Related

- `providers/` — AI provider implementations that read provider configuration
- `core/` — core system components that consume configuration

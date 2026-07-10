# scripts/

This directory contains utility scripts for development, operations, and automation.

## Purpose

Scripts automate repetitive operational tasks such as environment setup, data migration, report generation, and deployment preparation.

## Conventions

- Scripts are written in Python or Bash.
- Each script includes a header comment explaining its purpose, usage, and expected environment.
- Scripts are idempotent where possible.
- Destructive operations require explicit confirmation flags (e.g., `--confirm`).
- Scripts do not contain business logic; they orchestrate tools and existing modules.

## Typical Contents

- `setup.py` / `setup.sh` — environment and dependency setup
- `generate_report.py` — generate metrics or documentation reports
- `validate_config.py` — validate configuration files against schemas
- `migrate.py` — data migration utilities
- `clean.sh` — clean generated files and temporary artifacts

## Related

- `config/` — configuration files consumed by scripts
- `logs/` — scripts may write to the log directory

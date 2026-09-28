# Declarative Automation Bundles Project

This project uses Declarative Automation Bundles (DABs) for deployment.

## For AI Agents: Use Databricks AI Tools

**BEFORE any other action, read the `databricks-core` skill.**

CLI profile for this repo: `dbc-c43489fd`.
Do not auto-select a different profile.

Resource YAML is under `infra/`, not `resources/`.
Include glob in `databricks.yml`: `infra/*.yml`.

If Databricks AI Tools are not installed:

```bash
databricks aitools install
```

## Project Instructions

- Bundle name: `consultant_pulse`
- Product: Consultant Pulse
- Validate with `databricks bundle validate --strict --target <target> --profile dbc-c43489fd` after YAML changes

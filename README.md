# Consultant Pulse

Databricks app to track feedback on individual consultants and provide evidence-based information for business and performance reviews.

Declarative Automation Bundle for TPM / consultant feedback on Databricks.

## Layout

```
consultant_pulse/
├── databricks.yml
├── .github/workflows/
├── docs/
│   ├── design.md
│   ├── architecture.md
│   └── decisions.md
├── src/
│   ├── consultant_pulse/
│   └── notebooks/
├── tests/
├── infra/
└── .gitignore
```

- `src/consultant_pulse/` — configuration, Databricks client, bronze model, and application API
- `src/notebooks/` — ingest notebook that creates `feedback_bronze` and writes the seed row
- `infra/` — DAB resource definitions (schema, volume, job)
- `tests/` — unit tests
- `.github/workflows/` — pull-request checks and a manual dev deploy

## Configuration

| Variable | Default |
| --- | --- |
| `CONSULTANT_PULSE_CATALOG` | `workspace` |
| `CONSULTANT_PULSE_SCHEMA` | `consultant_pulse` |
| `CONSULTANT_PULSE_VOLUME` | `feedback_raw` |
| `CONSULTANT_PULSE_BRONZE_TABLE` | `feedback_bronze` |
| `DATABRICKS_HOST` | `https://dbc-c43489fd-406c.cloud.databricks.com` |
| `DATABRICKS_CONFIG_PROFILE` | `dbc-c43489fd` |
| `DATABRICKS_WAREHOUSE_ID` | unset |

Service-principal variables `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET` are read only when opening a client. They are not stored on `Settings`.

## Prerequisites

- Databricks CLI >= 0.292.0 (this machine has v1.14.0)
- Profile `dbc-c43489fd` (workspace `https://dbc-c43489fd-406c.cloud.databricks.com`)

## Deploy

```bash
databricks bundle validate --strict --target dev --profile dbc-c43489fd
databricks bundle deploy --target dev --profile dbc-c43489fd
databricks bundle run ingest_feedback --target dev --profile dbc-c43489fd
```

Production:

```bash
databricks bundle deploy --target prod --profile dbc-c43489fd
```

## Local tests

```bash
uv sync --dev
uv run ruff check .
uv run pytest
```

Local config and DDL check:

```bash
uv run consultant-pulse --show-config
uv run consultant-pulse --bronze-ddl
```

## GitHub

Pull requests run `ruff`, `pytest`, and `databricks bundle validate --strict --target dev`.

Repository secrets, also stored locally in gitignored `.env`:

- `DATABRICKS_HOST` = `https://dbc-c43489fd-406c.cloud.databricks.com`
- `DATABRICKS_CLIENT_ID`
- `DATABRICKS_CLIENT_SECRET`

Dev deploy is the manual **Deploy dev** workflow. Production deploy stays the local command above.

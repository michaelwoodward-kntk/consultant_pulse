# Architecture

```
consultant_pulse
├── databricks.yml      # Bundle name, variables, dev/prod targets
├── infra/              # DAB resource YAML (jobs, schema, volume)
├── src/consultant_pulse/
│   ├── config.py       # Environment settings
│   ├── client.py       # Workspace client
│   ├── models.py       # Bronze contract and DDL
│   ├── api.py          # Application API
│   └── transform.py    # Score normalization
├── src/notebooks/      # Ingest notebook
├── tests/              # Unit tests
├── .github/workflows/  # Pull-request CI and manual dev deploy
└── docs/               # Design, architecture, decisions
```

## Runtime

| Layer | Choice |
| --- | --- |
| Workspace | `dbc-c43489fd` (`https://dbc-c43489fd-406c.cloud.databricks.com`) |
| Catalog (dev/prod) | `workspace` |
| Schema (dev) | Deployer's short name. Development mode does not add a second prefix. |
| Schema (prod) | `consultant_pulse` |
| Compute | Serverless job environment version 4 |
| SQL warehouse lookup | `Serverless Starter Warehouse` |

## Deployed resources

- Schema `${catalog}.${schema}`
- Volume `${catalog}.${schema}.feedback_raw`
- Job `ingest_feedback` → notebook `src/notebooks/ingest_feedback.py`
- Table `${catalog}.${schema}.feedback_bronze` (created on first job run)

## Application

`ConsultantPulseApi` reads `Settings`, prepares a feedback row, and returns bronze DDL. `connect` builds a Databricks workspace client. Local calls use profile `dbc-c43489fd`. CI calls use `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, and `DATABRICKS_CLIENT_SECRET`. The bundle file pins the workspace host and leaves the profile to the CLI flag so those environment variables work in GitHub Actions.

## Path rules

Resource YAML lives in `infra/`, so notebook paths are `../src/...`.

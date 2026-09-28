# Decisions

## ADR-001 — Bundle lives in `consultant_pulse`

The project name is `consultant_pulse`. The workspace folder, bundle key, and production schema use that name so CLI paths and workspace `.bundle` folders match the product. TPM feedback describes the data the product captures.

## ADR-002 — Resource YAML in `infra/`

Standard DAB templates use `resources/`. This repo uses `infra/` as requested. `databricks.yml` includes `infra/*.yml`. File names still follow `<name>.<resource_type>.yml`.

## ADR-003 — `workspace` catalog

The workspace currently has `workspace` and `financial_platform`. Feedback is not financial-platform data, so resources target `workspace`. Change `variables.catalog` per target if a dedicated catalog is created later.

## ADR-004 — Serverless job environments

The ingest job uses a serverless environment instead of a classic cluster so local deploy does not require choosing a `node_type_id`.

## ADR-005 — Dev schema is the user short name

Development mode prefixes Unity Catalog schema names. The dev target already sets the schema to the deployer short name, so the bundle sets `experimental.skip_name_prefix_for_schema` and the deployed dev schema stays that short name.

## ADR-006 — Host in the bundle, profile on the CLI

`databricks.yml` pins the workspace host and does not pin `workspace.profile` or service-principal credentials. Local commands pass `--profile dbc-c43489fd`. GitHub Actions authenticates with `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, and `DATABRICKS_CLIENT_SECRET`. Pull requests run unit tests and strict dev validation. Dev deploy is a manual workflow. Prod deploy stays a local command.

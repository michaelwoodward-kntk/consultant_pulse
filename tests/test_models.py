from pathlib import Path

import pytest

from consultant_pulse.config import Settings
from consultant_pulse.models import SEED_FEEDBACK_ID, bronze_create_sql, quote_identifier, volume_path


def _settings(**overrides: str) -> Settings:
    base = {
        "catalog": "workspace",
        "schema": "consultant_pulse",
        "volume": "feedback_raw",
        "bronze_table": "feedback_bronze",
        "host": "https://dbc-c43489fd-406c.cloud.databricks.com",
        "profile": "dbc-c43489fd",
    }
    base.update(overrides)
    return Settings(**base)


def test_bronze_ddl_quotes_identifiers_and_lists_columns():
    sql = bronze_create_sql(_settings())

    assert sql.startswith(
        "CREATE TABLE IF NOT EXISTS `workspace`.`consultant_pulse`.`feedback_bronze`"
    )
    assert "`score` DOUBLE" in sql
    assert "`submitted_at` TIMESTAMP" in sql
    assert sql.endswith("USING DELTA")


def test_quote_identifier_rejects_sql_fragments():
    with pytest.raises(ValueError):
        quote_identifier("workspace; drop")
    with pytest.raises(ValueError):
        bronze_create_sql(_settings(schema="tpm.feedback"))


def test_volume_path():
    assert volume_path(_settings()) == "/Volumes/workspace/consultant_pulse/feedback_raw"


def test_notebook_uses_the_seed_contract():
    notebook = Path("src/notebooks/ingest_feedback.py").read_text(encoding="utf-8")
    assert SEED_FEEDBACK_ID in notebook

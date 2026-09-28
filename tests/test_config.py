from consultant_pulse.config import (
    DEFAULT_BRONZE_TABLE,
    DEFAULT_CATALOG,
    DEFAULT_HOST,
    DEFAULT_PROFILE,
    DEFAULT_SCHEMA,
    DEFAULT_VOLUME,
    Settings,
)


def test_from_env_uses_defaults_when_empty():
    settings = Settings.from_env({})

    assert settings.catalog == DEFAULT_CATALOG
    assert settings.schema == DEFAULT_SCHEMA
    assert settings.volume == DEFAULT_VOLUME
    assert settings.bronze_table == DEFAULT_BRONZE_TABLE
    assert settings.host == DEFAULT_HOST
    assert settings.profile == DEFAULT_PROFILE
    assert settings.warehouse_id is None


def test_from_env_reads_overrides():
    settings = Settings.from_env(
        {
            "CONSULTANT_PULSE_CATALOG": "workspace",
            "CONSULTANT_PULSE_SCHEMA": "lab",
            "CONSULTANT_PULSE_VOLUME": "landing",
            "CONSULTANT_PULSE_BRONZE_TABLE": "feedback_bronze",
            "DATABRICKS_HOST": "https://example.cloud.databricks.com",
            "DATABRICKS_CONFIG_PROFILE": "ci",
            "DATABRICKS_WAREHOUSE_ID": "abc123",
        }
    )

    assert settings.schema == "lab"
    assert settings.volume == "landing"
    assert settings.host == "https://example.cloud.databricks.com"
    assert settings.profile == "ci"
    assert settings.warehouse_id == "abc123"


def test_blank_env_values_fall_back_to_defaults():
    settings = Settings.from_env({"CONSULTANT_PULSE_SCHEMA": "  ", "DATABRICKS_WAREHOUSE_ID": ""})

    assert settings.schema == DEFAULT_SCHEMA
    assert settings.warehouse_id is None

"""Runtime settings for Consultant Pulse.

Bundle targets still own the deployed catalog and schema. This module is the
local and CI view of those same names, read from the environment.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_HOST = "https://dbc-c43489fd-406c.cloud.databricks.com"
DEFAULT_PROFILE = "dbc-c43489fd"
DEFAULT_CATALOG = "workspace"
DEFAULT_SCHEMA = "consultant_pulse"
DEFAULT_VOLUME = "feedback_raw"
DEFAULT_BRONZE_TABLE = "feedback_bronze"


def _value(env: Mapping[str, str], key: str, default: str) -> str:
    raw = env.get(key)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip()


def _optional(env: Mapping[str, str], key: str) -> str | None:
    raw = env.get(key)
    if raw is None or raw.strip() == "":
        return None
    return raw.strip()


@dataclass(frozen=True)
class Settings:
    """Connection and Unity Catalog names. Secrets stay in the process environment."""

    catalog: str
    schema: str
    volume: str
    bronze_table: str
    host: str
    profile: str
    warehouse_id: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        source = os.environ if env is None else env
        return cls(
            catalog=_value(source, "CONSULTANT_PULSE_CATALOG", DEFAULT_CATALOG),
            schema=_value(source, "CONSULTANT_PULSE_SCHEMA", DEFAULT_SCHEMA),
            volume=_value(source, "CONSULTANT_PULSE_VOLUME", DEFAULT_VOLUME),
            bronze_table=_value(source, "CONSULTANT_PULSE_BRONZE_TABLE", DEFAULT_BRONZE_TABLE),
            host=_value(source, "DATABRICKS_HOST", DEFAULT_HOST),
            profile=_value(source, "DATABRICKS_CONFIG_PROFILE", DEFAULT_PROFILE),
            warehouse_id=_optional(source, "DATABRICKS_WAREHOUSE_ID"),
        )

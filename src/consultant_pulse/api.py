"""Application API for Consultant Pulse.

Callers use this module to read configuration, prepare a feedback row, and
build the bronze DDL. It does not open a warehouse connection until
``client`` is called.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from consultant_pulse.client import connect
from consultant_pulse.config import Settings
from consultant_pulse.models import (
    BRONZE_COLUMNS,
    REQUIRED_COLUMNS,
    FeedbackRecord,
    bronze_create_sql,
    qualified_name,
    volume_path,
)
from consultant_pulse.transform import normalize_score


class FeedbackValidationError(ValueError):
    """A feedback row is missing a required field or has the wrong type."""


class ConsultantPulseApi:
    def __init__(self, settings: Settings | None = None, *, connector: Any = connect) -> None:
        self.settings = settings or Settings.from_env()
        self._connector = connector

    def describe(self) -> dict[str, Any]:
        settings = self.settings
        return {
            "catalog": settings.catalog,
            "schema": settings.schema,
            "volume": settings.volume,
            "volume_path": volume_path(settings),
            "bronze_table": qualified_name(settings.catalog, settings.schema, settings.bronze_table),
            "columns": [column.name for column in BRONZE_COLUMNS],
            "host": settings.host,
            "profile": settings.profile,
            "warehouse_id": settings.warehouse_id,
        }

    def bronze_ddl(self) -> str:
        return bronze_create_sql(self.settings)

    def prepare_feedback(self, row: Mapping[str, Any]) -> FeedbackRecord:
        missing = [name for name in REQUIRED_COLUMNS if name not in row]
        if missing:
            raise FeedbackValidationError(f"Missing columns: {', '.join(missing)}")

        feedback_id = _require_str(row, "feedback_id")
        consultant_name = _require_str(row, "consultant_name")
        engagement = _require_str(row, "engagement")
        submitted_at = _optional_datetime(row.get("submitted_at"))
        score = _optional_number(row.get("score"))
        comment = _optional_str(row.get("comment"))

        return FeedbackRecord(
            feedback_id=feedback_id,
            consultant_name=consultant_name,
            engagement=engagement,
            submitted_at=submitted_at,
            score=normalize_score(score),
            comment=comment,
        )

    def client(self) -> Any:
        return self._connector(self.settings)


def _require_str(row: Mapping[str, Any], name: str) -> str:
    value = row[name]
    if not isinstance(value, str) or value.strip() == "":
        raise FeedbackValidationError(f"{name} must be a non-empty string")
    return value


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise FeedbackValidationError("comment must be a string or null")
    return value


def _optional_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FeedbackValidationError("score must be a number or null")
    return float(value)


def _optional_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, datetime):
        raise FeedbackValidationError("submitted_at must be a datetime or null")
    return value

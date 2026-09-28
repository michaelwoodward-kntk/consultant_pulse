from datetime import UTC, datetime

import pytest

from consultant_pulse.api import ConsultantPulseApi, FeedbackValidationError
from consultant_pulse.config import Settings


def _api() -> ConsultantPulseApi:
    return ConsultantPulseApi(
        Settings(
            catalog="workspace",
            schema="consultant_pulse",
            volume="feedback_raw",
            bronze_table="feedback_bronze",
            host="https://dbc-c43489fd-406c.cloud.databricks.com",
            profile="dbc-c43489fd",
            warehouse_id="wh-1",
        )
    )


def test_prepare_feedback_normalizes_score():
    record = _api().prepare_feedback(
        {
            "feedback_id": "row-1",
            "consultant_name": "Ada",
            "engagement": "Northwind",
            "submitted_at": datetime(2026, 9, 28, tzinfo=UTC),
            "score": 9,
            "comment": "Clear plan",
        }
    )

    assert record.score == 5.0
    assert record.comment == "Clear plan"


def test_prepare_feedback_rejects_missing_and_bad_types():
    api = _api()
    with pytest.raises(FeedbackValidationError, match="comment"):
        api.prepare_feedback(
            {
                "feedback_id": "row-1",
                "consultant_name": "Ada",
                "engagement": "Northwind",
                "submitted_at": None,
                "score": 4,
            }
        )
    with pytest.raises(FeedbackValidationError, match="score"):
        api.prepare_feedback(
            {
                "feedback_id": "row-1",
                "consultant_name": "Ada",
                "engagement": "Northwind",
                "submitted_at": None,
                "score": "high",
                "comment": None,
            }
        )


def test_describe_names_the_bronze_table():
    described = _api().describe()

    assert described["bronze_table"] == "`workspace`.`consultant_pulse`.`feedback_bronze`"
    assert described["columns"] == [
        "feedback_id",
        "consultant_name",
        "engagement",
        "submitted_at",
        "score",
        "comment",
    ]
    assert described["warehouse_id"] == "wh-1"
    assert "secret" not in described

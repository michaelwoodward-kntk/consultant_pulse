"""Shared transforms for TPM feedback rows."""

from __future__ import annotations

from consultant_pulse.models import REQUIRED_COLUMNS

__all__ = ["REQUIRED_COLUMNS", "normalize_score"]


def normalize_score(score: float | None) -> float | None:
    """Clamp a 1–5 score and round to one decimal place."""
    if score is None:
        return None
    value = float(score)
    return round(min(5.0, max(1.0, value)), 1)

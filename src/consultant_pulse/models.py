"""Unity Catalog names and the bronze feedback contract."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from consultant_pulse.config import Settings

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_COLUMN_TYPES = frozenset({"STRING", "DOUBLE", "TIMESTAMP"})


def quote_identifier(identifier: str) -> str:
    """Backtick-quote a Unity Catalog identifier.

    Rejects anything other than a plain name so catalog, schema, and table
    values cannot change the SQL statement.
    """
    if not _IDENTIFIER.fullmatch(identifier):
        raise ValueError(f"Invalid identifier: {identifier!r}")
    return f"`{identifier}`"


@dataclass(frozen=True)
class Column:
    name: str
    data_type: str

    def __post_init__(self) -> None:
        quote_identifier(self.name)
        if self.data_type not in _COLUMN_TYPES:
            raise ValueError(f"Unsupported column type: {self.data_type}")


BRONZE_COLUMNS: tuple[Column, ...] = (
    Column("feedback_id", "STRING"),
    Column("consultant_name", "STRING"),
    Column("engagement", "STRING"),
    Column("submitted_at", "TIMESTAMP"),
    Column("score", "DOUBLE"),
    Column("comment", "STRING"),
)

REQUIRED_COLUMNS: tuple[str, ...] = tuple(column.name for column in BRONZE_COLUMNS)

SEED_FEEDBACK_ID = "seed-0001"


def qualified_name(catalog: str, schema: str, name: str) -> str:
    return ".".join(quote_identifier(part) for part in (catalog, schema, name))


def volume_path(settings: Settings) -> str:
    parts = (settings.catalog, settings.schema, settings.volume)
    for part in parts:
        quote_identifier(part)
    return "/Volumes/" + "/".join(parts)


def bronze_create_sql(settings: Settings) -> str:
    table = qualified_name(settings.catalog, settings.schema, settings.bronze_table)
    columns = ",\n".join(
        f"  {quote_identifier(column.name)} {column.data_type}" for column in BRONZE_COLUMNS
    )
    return f"CREATE TABLE IF NOT EXISTS {table} (\n{columns}\n)\nUSING DELTA"


@dataclass(frozen=True)
class FeedbackRecord:
    feedback_id: str
    consultant_name: str
    engagement: str
    submitted_at: datetime | None
    score: float | None
    comment: str | None

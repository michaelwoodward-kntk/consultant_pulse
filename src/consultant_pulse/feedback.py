"""TPM submission of project feedback.

A TPM identifies the project and the consultant, writes the feedback, and
submits it. The record is stamped in UTC and kept with that project and
consultant. Submitted feedback stays as written unless the active workflow
permits an edit.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

Clock = Callable[[], datetime]
IdFactory = Callable[[], str]


class FeedbackSubmissionError(ValueError):
    """The submission does not identify a project, a consultant, and feedback."""


class FeedbackEditNotPermitted(Exception):
    """Submitted feedback cannot be changed under the active workflow."""


class FeedbackNotFound(KeyError):
    """No submitted feedback exists for this id."""


@dataclass(frozen=True)
class SubmittedFeedback:
    """One immutable observation tied to a project and a consultant."""

    feedback_id: str
    project_id: str
    consultant_id: str
    feedback: str
    submitted_at: datetime
    updated_at: datetime
    submitted_by_name: str
    submitted_by_email: str


@dataclass(frozen=True)
class FeedbackWorkflow:
    """Whether submitted feedback may be changed.

    The default workflow does not permit edits. A later workflow can allow
    them with ``allow_edits`` or by overriding ``permits_edit``.
    """

    allow_edits: bool = False

    def permits_edit(self, record: SubmittedFeedback) -> bool:
        return self.allow_edits


class FeedbackStore:
    """Insert-only record of submitted feedback."""

    def __init__(self) -> None:
        self._records: dict[str, SubmittedFeedback] = {}

    def add(self, record: SubmittedFeedback) -> SubmittedFeedback:
        if record.feedback_id in self._records:
            raise FeedbackEditNotPermitted("This feedback cannot be edited after submission.")
        self._records[record.feedback_id] = record
        return record

    def get(self, feedback_id: str) -> SubmittedFeedback:
        try:
            return self._records[feedback_id]
        except KeyError as exc:
            raise FeedbackNotFound(feedback_id) from exc

    def replace(self, record: SubmittedFeedback, workflow: FeedbackWorkflow) -> SubmittedFeedback:
        current = self.get(record.feedback_id)
        if not workflow.permits_edit(current):
            raise FeedbackEditNotPermitted("This feedback cannot be edited after submission.")
        if (record.project_id, record.consultant_id, record.submitted_at) != (
            current.project_id,
            current.consultant_id,
            current.submitted_at,
        ):
            raise FeedbackEditNotPermitted(
                "The project, consultant, and submission time stay with the original feedback."
            )
        self._records[record.feedback_id] = record
        return record

    def for_project_and_consultant(
        self, project_id: str, consultant_id: str
    ) -> tuple[SubmittedFeedback, ...]:
        return tuple(
            record
            for record in self._records.values()
            if record.project_id == project_id and record.consultant_id == consultant_id
        )


class FeedbackService:
    """Accept a TPM's project feedback and keep the submitted record."""

    def __init__(
        self,
        store: FeedbackStore | None = None,
        workflow: FeedbackWorkflow | None = None,
        *,
        clock: Clock | None = None,
        id_factory: IdFactory | None = None,
    ) -> None:
        self.store = store or FeedbackStore()
        self.workflow = workflow or FeedbackWorkflow()
        self._clock = clock or _utc_now
        self._id_factory = id_factory or _new_id

    def submit(
        self,
        *,
        project_id: str,
        consultant_id: str,
        feedback: str,
        submitted_by_name: str,
        submitted_by_email: str,
    ) -> SubmittedFeedback:
        """Record feedback for one consultant on one project."""
        submitted_at = _as_utc(self._clock())
        record = SubmittedFeedback(
            feedback_id=self._id_factory(),
            project_id=_require_text(project_id, "Identify the project before submitting feedback."),
            consultant_id=_require_text(
                consultant_id, "Identify the consultant before submitting feedback."
            ),
            feedback=_require_text(feedback, "Enter the feedback before submitting."),
            submitted_at=submitted_at,
            updated_at=submitted_at,
            submitted_by_name=_require_text(
                submitted_by_name, "Enter your name before submitting feedback."
            ),
            submitted_by_email=_require_text(
                submitted_by_email, "Enter your email before submitting feedback."
            ),
        )
        return self.store.add(record)

    def edit(self, feedback_id: str, *, feedback: str) -> SubmittedFeedback:
        """Replace the feedback text when the workflow allows it.

        The project, consultant, and original submission time stay the same.
        """
        current = self.store.get(feedback_id)
        if not self.workflow.permits_edit(current):
            raise FeedbackEditNotPermitted("This feedback cannot be edited after submission.")
        updated = SubmittedFeedback(
            feedback_id=current.feedback_id,
            project_id=current.project_id,
            consultant_id=current.consultant_id,
            feedback=_require_text(feedback, "Enter the feedback before submitting."),
            submitted_at=current.submitted_at,
            updated_at=_as_utc(self._clock()),
            submitted_by_name=current.submitted_by_name,
            submitted_by_email=current.submitted_by_email,
        )
        return self.store.replace(updated, self.workflow)


def _require_text(value: str, message: str) -> str:
    if not isinstance(value, str):
        raise FeedbackSubmissionError(message)
    text = value.strip()
    if text == "":
        raise FeedbackSubmissionError(message)
    return text


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _new_id() -> str:
    return str(uuid4())

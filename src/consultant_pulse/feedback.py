"""TPM submission of project feedback, and a manager's view of it.

A TPM identifies the project and the consultant, writes the feedback, and
submits it. The record is stamped in UTC and kept with that project and
consultant. Submitted feedback stays as written unless the active workflow
permits an edit.

A manager can view the documented observations for one consultant: how many
there are, which projects and TPMs they come from, and when the latest one
was submitted. Counts are observation counts, not performance scores.
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
class TpmContributor:
    """A TPM who submitted at least one observation for the consultant."""

    name: str
    email: str


@dataclass(frozen=True)
class ProjectFeedbackGroup:
    """Documented observations for one project, oldest submission first."""

    project_id: str
    observations: tuple[SubmittedFeedback, ...]

    @property
    def observation_count(self) -> int:
        return len(self.observations)


@dataclass(frozen=True)
class ConsultantFeedbackAggregate:
    """Documented observations for one consultant.

    ``observation_count`` is the number of submitted records. It is not a
    performance score.
    """

    consultant_id: str
    observations: tuple[SubmittedFeedback, ...]
    by_project: tuple[ProjectFeedbackGroup, ...]
    tpms: tuple[TpmContributor, ...]
    last_submitted_at: datetime | None

    @property
    def observation_count(self) -> int:
        return len(self.observations)

    @property
    def project_count(self) -> int:
        return len(self.by_project)

    @property
    def tpm_count(self) -> int:
        return len(self.tpms)


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

    def for_consultant(self, consultant_id: str) -> tuple[SubmittedFeedback, ...]:
        return tuple(record for record in self._records.values() if record.consultant_id == consultant_id)


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

    def aggregate_for_consultant(self, consultant_id: str) -> ConsultantFeedbackAggregate:
        """Summarize documented observations for one consultant.

        Observations are oldest first. Project groups follow project id.
        TPM contributors follow the first time each email appears.
        """
        consultant_id = _require_text(
            consultant_id, "Identify the consultant before viewing feedback."
        )
        observations = tuple(
            sorted(
                self.store.for_consultant(consultant_id),
                key=lambda record: (record.submitted_at, record.feedback_id),
            )
        )
        grouped: dict[str, list[SubmittedFeedback]] = {}
        for record in observations:
            grouped.setdefault(record.project_id, []).append(record)
        by_project = tuple(
            ProjectFeedbackGroup(project_id=project_id, observations=tuple(items))
            for project_id, items in sorted(grouped.items())
        )
        tpms: list[TpmContributor] = []
        seen_emails: set[str] = set()
        for record in observations:
            if record.submitted_by_email in seen_emails:
                continue
            seen_emails.add(record.submitted_by_email)
            tpms.append(TpmContributor(name=record.submitted_by_name, email=record.submitted_by_email))
        last_submitted_at = observations[-1].submitted_at if observations else None
        return ConsultantFeedbackAggregate(
            consultant_id=consultant_id,
            observations=observations,
            by_project=by_project,
            tpms=tuple(tpms),
            last_submitted_at=last_submitted_at,
        )


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

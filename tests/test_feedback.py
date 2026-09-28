from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from consultant_pulse.feedback import (
    FeedbackEditNotPermitted,
    FeedbackService,
    FeedbackStore,
    FeedbackSubmissionError,
    FeedbackWorkflow,
    SubmittedFeedback,
)


def _service(**kwargs: object) -> FeedbackService:
    return FeedbackService(**kwargs)  # type: ignore[arg-type]


def _submit(service: FeedbackService, **overrides: str) -> SubmittedFeedback:
    payload = {
        "project_id": "project-abc",
        "consultant_id": "consultant-alex",
        "feedback": "Alex redesigned the streaming pipeline and brought the job back on schedule.",
        "submitted_by_name": "Jordan Lee",
        "submitted_by_email": "jordan.lee@example.com",
    }
    payload.update(overrides)
    return service.submit(**payload)  # type: ignore[arg-type]


def test_submit_records_project_consultant_feedback_and_utc_timestamp():
    moment = datetime(2026, 9, 28, 18, 30, tzinfo=UTC)
    service = _service(clock=lambda: moment, id_factory=lambda: "feedback-1")

    record = _submit(service)

    assert record.feedback_id == "feedback-1"
    assert record.project_id == "project-abc"
    assert record.consultant_id == "consultant-alex"
    assert record.feedback.startswith("Alex redesigned")
    assert record.submitted_at == moment
    assert record.updated_at == moment
    assert record.submitted_at.tzinfo == UTC
    assert record.submitted_by_name == "Jordan Lee"


def test_submit_strips_identifiers_and_rejects_blank_feedback():
    service = _service(clock=lambda: datetime(2026, 9, 28, tzinfo=UTC), id_factory=lambda: "feedback-1")

    record = _submit(service, project_id="  project-abc  ", consultant_id="  consultant-alex  ")
    assert record.project_id == "project-abc"
    assert record.consultant_id == "consultant-alex"

    with pytest.raises(FeedbackSubmissionError, match="project"):
        _submit(service, project_id="   ")
    with pytest.raises(FeedbackSubmissionError, match="consultant"):
        _submit(service, consultant_id="")
    with pytest.raises(FeedbackSubmissionError, match="feedback"):
        _submit(service, feedback=" \n\t ")
    with pytest.raises(FeedbackSubmissionError, match="name"):
        _submit(service, submitted_by_name=" ")


def test_feedback_is_associated_with_its_project_and_consultant():
    service = _service(
        clock=lambda: datetime(2026, 9, 28, tzinfo=UTC),
        id_factory=iter(["feedback-1", "feedback-2", "feedback-3"]).__next__,
    )
    first = _submit(service)
    second = _submit(service, feedback="Follow-up on the same engagement.")
    _submit(service, project_id="project-xyz", consultant_id="consultant-chris")

    matched = service.store.for_project_and_consultant("project-abc", "consultant-alex")
    other = service.store.for_project_and_consultant("project-abc", "consultant-chris")

    assert matched == (first, second)
    assert other == ()


def test_submitted_feedback_cannot_be_edited_or_mutated():
    service = _service(clock=lambda: datetime(2026, 9, 28, tzinfo=UTC), id_factory=lambda: "feedback-1")
    record = _submit(service)

    with pytest.raises(FrozenInstanceError):
        record.feedback = "Changed after the fact."  # type: ignore[misc]

    with pytest.raises(FeedbackEditNotPermitted, match="cannot be edited"):
        service.edit("feedback-1", feedback="Changed after the fact.")

    assert service.store.get("feedback-1").feedback == record.feedback


def test_store_refuses_to_overwrite_a_submitted_record():
    store = FeedbackStore()
    moment = datetime(2026, 9, 28, tzinfo=UTC)
    original = SubmittedFeedback(
        feedback_id="feedback-1",
        project_id="project-abc",
        consultant_id="consultant-alex",
        feedback="Original observation.",
        submitted_at=moment,
        updated_at=moment,
        submitted_by_name="Jordan Lee",
        submitted_by_email="jordan.lee@example.com",
    )
    store.add(original)
    replacement = SubmittedFeedback(
        feedback_id="feedback-1",
        project_id="project-other",
        consultant_id="consultant-other",
        feedback="Replaced.",
        submitted_at=moment,
        updated_at=moment,
        submitted_by_name="Jordan Lee",
        submitted_by_email="jordan.lee@example.com",
    )

    with pytest.raises(FeedbackEditNotPermitted):
        store.add(replacement)

    assert store.get("feedback-1") == original


def test_edit_when_the_workflow_permits_keeps_project_consultant_and_timestamp():
    submitted_at = datetime(2026, 9, 28, 18, 0, tzinfo=UTC)
    edited_at = datetime(2026, 9, 28, 19, 0, tzinfo=UTC)
    moments = iter((submitted_at, edited_at))
    service = _service(
        workflow=FeedbackWorkflow(allow_edits=True),
        clock=lambda: next(moments),
        id_factory=lambda: "feedback-1",
    )
    original = _submit(service)

    updated = service.edit("feedback-1", feedback="  Corrected observation.  ")

    assert updated.feedback == "Corrected observation."
    assert updated.feedback_id == original.feedback_id
    assert updated.project_id == original.project_id
    assert updated.consultant_id == original.consultant_id
    assert updated.submitted_at == submitted_at
    assert updated.updated_at == edited_at
    assert service.store.get("feedback-1") == updated


def test_custom_workflow_decides_per_record():
    class AuthorOnly(FeedbackWorkflow):
        def permits_edit(self, record: SubmittedFeedback) -> bool:
            return record.submitted_by_email == "jordan.lee@example.com"

    service = _service(
        workflow=AuthorOnly(),
        clock=lambda: datetime(2026, 9, 28, tzinfo=UTC),
        id_factory=lambda: "feedback-1",
    )
    _submit(service)

    updated = service.edit("feedback-1", feedback="Author correction.")
    assert updated.feedback == "Author correction."

    denied = FeedbackService(
        store=service.store,
        workflow=AuthorOnly(),
        clock=lambda: datetime(2026, 9, 29, tzinfo=UTC),
        id_factory=lambda: "feedback-2",
    )
    denied.submit(
        project_id="project-abc",
        consultant_id="consultant-alex",
        feedback="A second observation.",
        submitted_by_name="Sam Patel",
        submitted_by_email="sam.patel@example.com",
    )
    with pytest.raises(FeedbackEditNotPermitted):
        denied.edit("feedback-2", feedback="Not the author.")

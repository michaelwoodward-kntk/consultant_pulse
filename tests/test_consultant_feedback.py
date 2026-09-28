from datetime import UTC, datetime, timedelta

import pytest

from consultant_pulse.feedback import (
    FeedbackService,
    FeedbackSubmissionError,
    FeedbackWorkflow,
    TpmContributor,
)


def _service(**kwargs: object) -> FeedbackService:
    return FeedbackService(**kwargs)  # type: ignore[arg-type]


def _submit_at(
    service: FeedbackService,
    moment: datetime,
    *,
    project_id: str,
    consultant_id: str,
    feedback: str,
    submitted_by_name: str,
    submitted_by_email: str,
) -> None:
    FeedbackService(
        store=service.store,
        workflow=service.workflow,
        clock=lambda: moment,
        id_factory=service._id_factory,
    ).submit(
        project_id=project_id,
        consultant_id=consultant_id,
        feedback=feedback,
        submitted_by_name=submitted_by_name,
        submitted_by_email=submitted_by_email,
    )


def test_manager_sees_aggregated_observations_for_one_consultant():
    base = datetime(2026, 9, 1, tzinfo=UTC)
    ids = iter(["feedback-1", "feedback-2", "feedback-3", "feedback-4"]).__next__
    service = _service(id_factory=ids)
    _submit_at(
        service,
        base,
        project_id="project-abc",
        consultant_id="consultant-alex",
        feedback="Took ownership of the streaming design.",
        submitted_by_name="Jordan Lee",
        submitted_by_email="jordan.lee@example.com",
    )
    _submit_at(
        service,
        base + timedelta(days=10),
        project_id="project-xyz",
        consultant_id="consultant-alex",
        feedback="Clarified the customer latency target with their engineers.",
        submitted_by_name="Jordan Lee",
        submitted_by_email="jordan.lee@example.com",
    )
    _submit_at(
        service,
        base + timedelta(days=20),
        project_id="project-abc",
        consultant_id="consultant-alex",
        feedback="Walked the team through the revised pipeline.",
        submitted_by_name="Sam Patel",
        submitted_by_email="sam.patel@example.com",
    )
    _submit_at(
        service,
        base + timedelta(days=5),
        project_id="project-abc",
        consultant_id="consultant-chris",
        feedback="This observation belongs to someone else.",
        submitted_by_name="Jordan Lee",
        submitted_by_email="jordan.lee@example.com",
    )

    aggregate = service.aggregate_for_consultant("  consultant-alex  ")

    assert aggregate.consultant_id == "consultant-alex"
    assert aggregate.observation_count == 3
    assert aggregate.project_count == 2
    assert aggregate.tpm_count == 2
    assert aggregate.last_submitted_at == base + timedelta(days=20)
    assert [record.feedback_id for record in aggregate.observations] == [
        "feedback-1",
        "feedback-2",
        "feedback-3",
    ]
    assert aggregate.tpms == (
        TpmContributor("Jordan Lee", "jordan.lee@example.com"),
        TpmContributor("Sam Patel", "sam.patel@example.com"),
    )
    assert [group.project_id for group in aggregate.by_project] == ["project-abc", "project-xyz"]
    abc, xyz = aggregate.by_project
    assert abc.observation_count == 2
    assert [record.feedback_id for record in abc.observations] == ["feedback-1", "feedback-3"]
    assert xyz.observation_count == 1
    assert xyz.observations[0].feedback.startswith("Clarified the customer")
    assert "someone else" not in " ".join(record.feedback for record in aggregate.observations)


def test_empty_consultant_has_no_observations():
    service = _service(clock=lambda: datetime(2026, 9, 28, tzinfo=UTC), id_factory=lambda: "feedback-1")
    service.submit(
        project_id="project-abc",
        consultant_id="consultant-alex",
        feedback="An observation.",
        submitted_by_name="Jordan Lee",
        submitted_by_email="jordan.lee@example.com",
    )

    aggregate = service.aggregate_for_consultant("consultant-chris")

    assert aggregate.observation_count == 0
    assert aggregate.project_count == 0
    assert aggregate.tpm_count == 0
    assert aggregate.last_submitted_at is None
    assert aggregate.observations == ()
    assert aggregate.by_project == ()
    assert aggregate.tpms == ()


def test_view_requires_a_consultant():
    service = _service()

    with pytest.raises(FeedbackSubmissionError, match="consultant"):
        service.aggregate_for_consultant("  ")


def test_aggregate_uses_current_text_and_original_submission_time():
    submitted_at = datetime(2026, 9, 18, tzinfo=UTC)
    edited_at = datetime(2026, 9, 19, tzinfo=UTC)
    moments = iter((submitted_at, edited_at))
    service = _service(
        workflow=FeedbackWorkflow(allow_edits=True),
        clock=lambda: next(moments),
        id_factory=lambda: "feedback-1",
    )
    service.submit(
        project_id="project-abc",
        consultant_id="consultant-alex",
        feedback="Original observation.",
        submitted_by_name="Jordan Lee",
        submitted_by_email="jordan.lee@example.com",
    )
    service.edit("feedback-1", feedback="Corrected observation.")

    aggregate = service.aggregate_for_consultant("consultant-alex")

    assert aggregate.observations[0].feedback == "Corrected observation."
    assert aggregate.last_submitted_at == submitted_at
    assert aggregate.observation_count == 1

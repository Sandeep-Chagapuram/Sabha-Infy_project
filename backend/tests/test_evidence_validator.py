import pytest
from app.ai.evidence_validator import EvidenceValidator
from app.models.task import ValidationStatus

def test_quote_exists_verifies_successfully():
    transcript = [
        {"id": "seg_101", "speaker_name": "Vikram", "text": "I will handle the end-to-end payment gateway load testing and share the benchmark report by this Friday."}
    ]
    res = EvidenceValidator.validate_task_claim(
        title="Execute payment gateway load testing",
        assignee_name="Vikram",
        deadline_text="by this Friday",
        source_quote="I will handle the end-to-end payment gateway load testing and share the benchmark report by this Friday.",
        transcript_segments=transcript
    )
    assert res.is_valid is True
    assert res.quote_found is True
    assert res.status == ValidationStatus.EVIDENCE_SUPPORTED
    assert res.matched_segment_id == "seg_101"

def test_hallucinated_quote_flagged_unverified():
    transcript = [
        {"id": "seg_101", "speaker_name": "Vikram", "text": "We should review our quarterly cloud hosting bill."}
    ]
    res = EvidenceValidator.validate_task_claim(
        title="Migrate microservices to Kubernetes",
        assignee_name="Vikram",
        deadline_text="tomorrow",
        source_quote="I will immediately migrate all our microservices to Kubernetes cluster by tomorrow.",
        transcript_segments=transcript
    )
    assert res.quote_found is False
    assert res.status == ValidationStatus.UNVERIFIED
    assert "QUOTE_NOT_FOUND_IN_TRANSCRIPT" in res.flags

def test_negation_conflict_flagged():
    transcript = [
        {"id": "seg_102", "speaker_name": "Rohan", "text": "I previously said I could finish the migration script, but actually I cannot proceed."}
    ]
    res = EvidenceValidator.validate_task_claim(
        title="Finish the database migration script",  # False affirmative claim
        assignee_name="Rohan",
        deadline_text=None,
        source_quote="actually I cannot proceed",
        transcript_segments=transcript
    )
    assert res.status == ValidationStatus.CONFLICTING
    assert "POTENTIAL_CONTRADICTION_NEGATION_IGNORED" in res.flags

def test_unassigned_task_preserves_none():
    transcript = [
        {"id": "seg_103", "speaker_name": "Priya", "text": "Who is handling EU GDPR compliance? We haven't assigned an owner for that yet."}
    ]
    res = EvidenceValidator.validate_task_claim(
        title="EU GDPR compliance sign-off",
        assignee_name=None,  # Properly unassigned
        deadline_text=None,
        source_quote="We haven't assigned an owner for that yet.",
        transcript_segments=transcript
    )
    assert res.is_valid is True
    assert res.quote_found is True

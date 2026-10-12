from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user, get_current_workspace_member
from app.models.user import User, WorkspaceMember
from app.models.meeting import Meeting, TranscriptSegment, MeetingStatus, MeetingInputSource, SegmentStatus
from app.models.intelligence import Decision, Risk, DecisionStatus, IntelligenceRecord, IntelligenceType
from app.schemas.intelligence import (
    MeetingAnalysisResult,
    DecisionResponse,
    RiskResponse,
    ResearchBriefResponse
)
from app.schemas.meeting import AnalysisOptions
from app.ai.pipeline import AnalysisPipeline
from app.ai.demo_samples import DEMO_SAMPLES_CATALOG
from app.meetings.transcript_parser import TranscriptParser
from app.ai.research_service import ResearchService

router = APIRouter()

@router.get("/workspaces/{workspace_id}/demo-samples")
def get_demo_samples(
    workspace_id: str,
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    """Returns catalog of realistic demonstration samples."""
    return list(DEMO_SAMPLES_CATALOG.values())

@router.post("/workspaces/{workspace_id}/demo-samples/{sample_id}/load")
def load_demo_sample(
    workspace_id: str,
    sample_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    sample = DEMO_SAMPLES_CATALOG.get(sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Demo sample not found.")

    meeting = Meeting(
        workspace_id=workspace_id,
        title=f"[DEMO] {sample['title']}",
        description=sample['description'],
        input_source=MeetingInputSource.PASTED_TRANSCRIPT,
        status=MeetingStatus.COMPLETED,
        meeting_date=datetime.fromisoformat(sample['meeting_date'].replace('Z', '+00:00')),
        timezone=sample['timezone'],
        project_context=f"{sample['project_context']} ({sample['id']})"
    )
    db.add(meeting)
    db.flush()

    parsed = TranscriptParser.parse_text(sample['transcript'])
    for seg in parsed:
        ts = TranscriptSegment(
            meeting_id=meeting.id,
            sequence_number=seg["sequence_number"],
            speaker_name=seg["speaker_name"],
            text=seg["text"],
            start_time=seg["start_time"],
            end_time=seg["end_time"],
            status=SegmentStatus.FINAL
        )
        db.add(ts)

    db.commit()
    db.refresh(meeting)

    return {
        "meeting_id": meeting.id,
        "title": meeting.title,
        "sample_id": sample_id,
        "segment_count": len(parsed),
        "message": f"Successfully loaded '{sample['title']}' demo transcript into workspace."
    }

@router.post("/workspaces/{workspace_id}/meetings/{meeting_id}/analyze", response_model=MeetingAnalysisResult)
async def analyze_meeting(
    workspace_id: str,
    meeting_id: str,
    options: AnalysisOptions = AnalysisOptions(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    """
    Triggers shared analysis pipeline (Context Sieve -> Qualcomm Model Router -> Evidence Validator).
    """
    return await AnalysisPipeline.analyze_meeting(
        db=db,
        meeting_id=meeting_id,
        workspace_id=workspace_id,
        depth=options.depth,
        force_recompute=options.force_recompute
    )

@router.post("/workspaces/{workspace_id}/meetings/{meeting_id}/research", response_model=ResearchBriefResponse)
async def run_research(
    workspace_id: str,
    meeting_id: str,
    question: str = Query(..., description="Research question extracted from conversation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.workspace_id == workspace_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    return await ResearchService.generate_research_brief(
        question=question,
        context=meeting.project_context
    )

@router.post("/workspaces/{workspace_id}/decisions/{decision_id}/confirm")
def confirm_decision(
    workspace_id: str,
    decision_id: str,
    confirm: bool = Query(True),
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    decision = db.query(Decision).filter(Decision.id == decision_id, Decision.workspace_id == workspace_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found.")

    decision.status = DecisionStatus.CONFIRMED if confirm else DecisionStatus.DISPUTED
    db.commit()
    return {"message": f"Decision marked as {decision.status.value}"}

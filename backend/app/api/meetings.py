from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.api.deps import get_db, get_current_user, get_current_workspace_member
from app.models.user import User, WorkspaceMember
from app.models.meeting import Meeting, MeetingParticipant, MeetingStatus, MeetingInputSource, TranscriptSegment
from app.models.task import Task
from app.models.intelligence import Decision
from app.schemas.meeting import (
    MeetingCreate,
    MeetingResponse,
    MeetingDetailResponse,
    LiveKitTokenResponse,
    MeetingParticipantResponse
)
from app.meetings.livekit_service import LiveKitService
from app.core.config import settings

router = APIRouter()

@router.post("/workspaces/{workspace_id}/meetings", response_model=MeetingResponse)
def create_meeting(
    workspace_id: str,
    meeting_in: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    room_name = None
    if meeting_in.input_source == MeetingInputSource.LIVE_MEETING:
        room_name = f"sabha-{str(uuid.uuid4())[:12]}"

    meeting = Meeting(
        workspace_id=workspace_id,
        title=meeting_in.title,
        description=meeting_in.description,
        input_source=meeting_in.input_source,
        status=MeetingStatus.SCHEDULED if meeting_in.input_source == MeetingInputSource.LIVE_MEETING else MeetingStatus.COMPLETED,
        meeting_date=meeting_in.meeting_date or datetime.utcnow(),
        timezone=meeting_in.timezone or "UTC",
        project_context=meeting_in.project_context,
        livekit_room_name=room_name
    )
    db.add(meeting)
    db.flush()

    # Add host participant
    participant = MeetingParticipant(
        meeting_id=meeting.id,
        user_id=current_user.id,
        name=current_user.full_name,
        email=current_user.email,
        role="host"
    )
    db.add(participant)
    db.commit()
    db.refresh(meeting)

    return meeting

@router.get("/workspaces/{workspace_id}/meetings", response_model=List[MeetingResponse])
def list_meetings(
    workspace_id: str,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    return (
        db.query(Meeting)
        .filter(Meeting.workspace_id == workspace_id)
        .order_by(Meeting.created_at.desc())
        .all()
    )

@router.get("/workspaces/{workspace_id}/meetings/{meeting_id}", response_model=MeetingDetailResponse)
def get_meeting_detail(
    workspace_id: str,
    meeting_id: str,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.workspace_id == workspace_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    seg_count = db.query(TranscriptSegment).filter(TranscriptSegment.meeting_id == meeting_id).count()
    task_count = db.query(Task).filter(Task.meeting_id == meeting_id).count()
    dec_count = db.query(Decision).filter(Decision.meeting_id == meeting_id).count()

    participants_resp = [
        MeetingParticipantResponse.from_orm(p) for p in meeting.participants
    ]

    resp_dict = MeetingResponse.from_orm(meeting).dict()
    resp_dict["participants"] = participants_resp
    resp_dict["segment_count"] = seg_count
    resp_dict["task_count"] = task_count
    resp_dict["decision_count"] = dec_count

    return MeetingDetailResponse(**resp_dict)

@router.post("/workspaces/{workspace_id}/meetings/{meeting_id}/livekit-token", response_model=LiveKitTokenResponse)
def get_livekit_token(
    workspace_id: str,
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.workspace_id == workspace_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    if not meeting.livekit_room_name:
        meeting.livekit_room_name = f"sabha-{str(uuid.uuid4())[:12]}"
        db.commit()

    token = LiveKitService.generate_token(
        room_name=meeting.livekit_room_name,
        participant_identity=current_user.id,
        participant_name=current_user.full_name,
        can_publish=True,
        can_subscribe=True,
        is_admin=(member.role.value in ["host", "admin"])
    )

    return LiveKitTokenResponse(
        token=token,
        room_name=meeting.livekit_room_name,
        participant_identity=current_user.id,
        participant_name=current_user.full_name,
        server_url=settings.LIVEKIT_URL
    )

@router.post("/workspaces/{workspace_id}/meetings/{meeting_id}/end")
def end_meeting(
    workspace_id: str,
    meeting_id: str,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.workspace_id == workspace_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    meeting.status = MeetingStatus.COMPLETED
    db.commit()
    return {"message": "Meeting ended. Ready for intelligence analysis."}

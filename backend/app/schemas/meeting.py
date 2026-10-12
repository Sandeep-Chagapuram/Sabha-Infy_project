from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.meeting import MeetingInputSource, MeetingStatus
from app.schemas.transcript import TranscriptSegmentResponse

class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    input_source: MeetingInputSource = MeetingInputSource.LIVE_MEETING
    meeting_date: Optional[datetime] = None
    timezone: Optional[str] = "UTC"
    project_context: Optional[str] = None

class MeetingResponse(BaseModel):
    id: str
    workspace_id: str
    title: str
    description: Optional[str]
    input_source: MeetingInputSource
    status: MeetingStatus
    meeting_date: datetime
    timezone: str
    project_context: Optional[str]
    livekit_room_name: Optional[str]
    duration_seconds: int
    raw_token_count: int
    compressed_token_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MeetingParticipantCreate(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = "participant"

class MeetingParticipantResponse(BaseModel):
    id: str
    meeting_id: str
    user_id: Optional[str]
    name: str
    email: Optional[str]
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True

class MeetingDetailResponse(MeetingResponse):
    participants: List[MeetingParticipantResponse] = []
    segment_count: int = 0
    task_count: int = 0
    decision_count: int = 0

class LiveKitTokenResponse(BaseModel):
    token: str
    room_name: str
    participant_identity: str
    participant_name: str
    server_url: str

class AnalysisOptions(BaseModel):
    depth: str = "full"  # "essential", "full", "full_research"
    force_recompute: bool = False

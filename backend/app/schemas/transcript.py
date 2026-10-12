from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.meeting import SegmentStatus

class TranscriptSegmentCreate(BaseModel):
    sequence_number: int
    speaker_name: Optional[str] = None
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    status: SegmentStatus = SegmentStatus.FINAL

class TranscriptSegmentResponse(BaseModel):
    id: str
    meeting_id: str
    sequence_number: int
    speaker_name: Optional[str]
    text: str
    start_time: Optional[float]
    end_time: Optional[float]
    status: SegmentStatus
    created_at: datetime

    class Config:
        from_attributes = True

class TranscriptCorrectionCreate(BaseModel):
    corrected_text: str
    reason: Optional[str] = None

class TranscriptCorrectionResponse(BaseModel):
    id: str
    segment_id: str
    previous_text: str
    corrected_text: str
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PastedTranscriptRequest(BaseModel):
    title: str
    content: str
    meeting_date: Optional[str] = None  # ISO format string or YYYY-MM-DD
    timezone: Optional[str] = "UTC"
    participants: Optional[List[str]] = None
    project_context: Optional[str] = None
    analysis_depth: Optional[str] = "full"  # "essential", "full", "full_research"

class TokenCountEstimate(BaseModel):
    word_count: int
    char_count: int
    estimated_tokens: int
    estimated_cost_usd: float
    segment_count: int

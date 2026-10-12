from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class MeetingInputSource(str, enum.Enum):
    LIVE_MEETING = "live_meeting"
    PASTED_TRANSCRIPT = "pasted_transcript"
    UPLOADED_TRANSCRIPT = "uploaded_transcript"
    UPLOADED_AUDIO = "uploaded_audio"

class MeetingStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    FAILED = "failed"

class SegmentStatus(str, enum.Enum):
    PROVISIONAL = "provisional"
    FINAL = "final"

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    input_source = Column(SQLEnum(MeetingInputSource), default=MeetingInputSource.PASTED_TRANSCRIPT, nullable=False)
    status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.SCHEDULED, nullable=False)
    
    # Meeting metadata
    meeting_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    project_context = Column(Text, nullable=True)
    
    # LiveKit specific
    livekit_room_name = Column(String(100), unique=True, nullable=True)
    
    # Metrics
    duration_seconds = Column(Integer, default=0)
    raw_token_count = Column(Integer, default=0)
    compressed_token_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="meetings")
    participants = relationship("MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan")
    transcript_segments = relationship("TranscriptSegment", back_populates="meeting", cascade="all, delete-orphan", order_by="TranscriptSegment.sequence_number")
    tasks = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")
    intelligence_records = relationship("IntelligenceRecord", back_populates="meeting", cascade="all, delete-orphan")
    usage_records = relationship("AIUsageRecord", back_populates="meeting", cascade="all, delete-orphan")

class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    role = Column(String(50), default="participant")
    joined_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="participants")

class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=False)
    sequence_number = Column(Integer, nullable=False, index=True)
    speaker_name = Column(String(255), nullable=True)  # Null if speaker is unknown
    speaker_user_id = Column(String(36), nullable=True)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=True)  # seconds from start
    end_time = Column(Float, nullable=True)
    status = Column(SQLEnum(SegmentStatus), default=SegmentStatus.FINAL, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    meeting = relationship("Meeting", back_populates="transcript_segments")
    corrections = relationship("TranscriptCorrection", back_populates="segment", cascade="all, delete-orphan")

class TranscriptCorrection(Base):
    __tablename__ = "transcript_corrections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    segment_id = Column(String(36), ForeignKey("transcript_segments.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    previous_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    segment = relationship("TranscriptSegment", back_populates="corrections")

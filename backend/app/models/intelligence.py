from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime
from app.core.database import Base
from app.models.task import ValidationStatus

def generate_uuid():
    return str(uuid.uuid4())

class IntelligenceType(str, enum.Enum):
    SUMMARY = "summary"
    SECOND_BRAIN = "second_brain"
    DECISION = "decision"
    RISK = "risk"
    CREATIVE_SOLUTIONS = "creative_solutions"
    FLAW_DETECTION = "flaw_detection"
    RESEARCH_BRIEF = "research_brief"

class DecisionStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    PROPOSED = "proposed"
    DISPUTED = "disputed"

class RiskSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IntelligenceRecord(Base):
    __tablename__ = "intelligence_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=False)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    record_type = Column(SQLEnum(IntelligenceType), nullable=False)
    title = Column(String(255), nullable=False)
    content_json = Column(JSON, nullable=False)
    
    # Model attribution & provenance
    model_name = Column(String(100), nullable=False)
    pipeline_version = Column(String(20), default="1.0.0")
    source_segment_ids = Column(JSON, default=list)  # List of segment UUIDs
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.EVIDENCE_SUPPORTED)
    
    # Human Review
    is_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String(36), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="intelligence_records")

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=False)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(DecisionStatus), default=DecisionStatus.CONFIRMED, nullable=False)
    source_evidence_quote = Column(Text, nullable=False)
    source_segment_id = Column(String(36), nullable=True)
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.EVIDENCE_SUPPORTED)
    created_at = Column(DateTime, default=datetime.utcnow)

class Risk(Base):
    __tablename__ = "risks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=False)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(SQLEnum(RiskSeverity), default=RiskSeverity.MEDIUM, nullable=False)
    potential_impact = Column(Text, nullable=True)
    suggested_mitigation = Column(Text, nullable=True)
    source_evidence_quote = Column(Text, nullable=False)
    source_segment_id = Column(String(36), nullable=True)
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.EVIDENCE_SUPPORTED)
    created_at = Column(DateTime, default=datetime.utcnow)

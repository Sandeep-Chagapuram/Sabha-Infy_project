from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class TaskCategory(str, enum.Enum):
    DETERMINISTIC = "deterministic"
    ROUTINE_EXTRACTION = "routine_extraction"
    COMPLEX_REASONING = "complex_reasoning"
    RESEARCH = "research"
    CREATIVE = "creative"

class AIUsageRecord(Base):
    __tablename__ = "ai_usage_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=True)
    task_category = Column(SQLEnum(TaskCategory), nullable=False)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cached_tokens = Column(Integer, default=0)
    
    is_measured = Column(Boolean, default=True)  # True if directly reported by provider, False if estimated
    estimated_cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Integer, default=0)
    
    was_escalated = Column(Boolean, default=False)
    escalation_reason = Column(String(255), nullable=True)
    validation_passed = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="usage_records")

class BudgetLimit(Base):
    __tablename__ = "budget_limits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), unique=True, nullable=False)
    max_meeting_cost_usd = Column(Float, default=2.50)
    max_monthly_cost_usd = Column(Float, default=100.0)
    current_month_spent_usd = Column(Float, default=0.0)
    is_hard_stop = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=True)
    event_type = Column(String(100), nullable=False)  # e.g., "TASK_CONFIRMED", "MODEL_ESCALATED", "EXPORT_GENERATED"
    description = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

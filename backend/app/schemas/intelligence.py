from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.intelligence import IntelligenceType, DecisionStatus, RiskSeverity
from app.models.task import ValidationStatus

class DecisionResponse(BaseModel):
    id: str
    meeting_id: str
    workspace_id: str
    title: str
    description: str
    status: DecisionStatus
    source_evidence_quote: str
    source_segment_id: Optional[str]
    validation_status: ValidationStatus
    created_at: datetime

    class Config:
        from_attributes = True

class RiskResponse(BaseModel):
    id: str
    meeting_id: str
    workspace_id: str
    title: str
    description: str
    severity: RiskSeverity
    potential_impact: Optional[str]
    suggested_mitigation: Optional[str]
    source_evidence_quote: str
    source_segment_id: Optional[str]
    validation_status: ValidationStatus
    created_at: datetime

    class Config:
        from_attributes = True

class SecondBrainBelieveItem(BaseModel):
    item: str
    type: str  # "decision", "assumption", "plan", "commitment", "constraint"
    evidence_quote: str
    segment_id: Optional[str] = None
    validation_status: ValidationStatus = ValidationStatus.EVIDENCE_SUPPORTED

class SecondBrainMissingItem(BaseModel):
    finding: str
    concern_type: str
    evidence_quote: str
    reasoning: str
    potential_impact: str
    confidence: str
    suggested_verification: str
    recommended_mitigation: Optional[str] = None
    segment_id: Optional[str] = None

class SecondBrainInvestigateItem(BaseModel):
    recommendation: str
    action_type: str  # "experiment", "research", "decision", "validation"
    suggested_owner: Optional[str] = None
    rationale: str
    convertible_to_task: bool = True

class SecondBrainResponse(BaseModel):
    what_we_believe: List[SecondBrainBelieveItem]
    what_we_might_be_missing: List[SecondBrainMissingItem]
    what_to_investigate_next: List[SecondBrainInvestigateItem]
    model_name: str
    pipeline_version: str

class CreativeApproach(BaseModel):
    title: str
    explanation: str
    expected_benefits: List[str]
    limitations: List[str]
    required_resources: List[str]
    risks: List[str]
    assumptions: List[str]
    suggested_experiments: List[str]
    evaluation_criteria_scores: Dict[str, float] = {}

class CreativeSolutionsResponse(BaseModel):
    problem_statement: str
    approaches: List[CreativeApproach]
    model_name: str

class FlawFinding(BaseModel):
    title: str
    concern_type: str
    evidence_quote: str
    reasoning: str
    potential_impact: str
    confidence: str
    suggested_verification: str
    recommended_mitigation: Optional[str] = None

class FlawDetectionResponse(BaseModel):
    findings: List[FlawFinding]
    model_name: str

class ResearchSource(BaseModel):
    title: str
    url: str
    publication_date: Optional[str] = None
    retrieval_date: str
    excerpt: str

class ResearchBriefResponse(BaseModel):
    question: str
    summary: str
    key_findings: List[str]
    sources: List[ResearchSource]
    uncertainty_and_limitations: str
    suggested_follow_ups: List[str]
    model_name: str

class MeetingAnalysisResult(BaseModel):
    meeting_id: str
    status: str
    executive_summary: str
    decisions: List[DecisionResponse]
    risks: List[RiskResponse]
    second_brain: Optional[SecondBrainResponse] = None
    creative_solutions: Optional[CreativeSolutionsResponse] = None
    flaw_detection: Optional[FlawDetectionResponse] = None
    research_briefs: List[ResearchBriefResponse] = []
    tokens_raw: int
    tokens_compressed: int
    compression_ratio: float
    estimated_cost_usd: float
    model_used: str

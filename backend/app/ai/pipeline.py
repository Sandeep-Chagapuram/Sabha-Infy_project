import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.meeting import Meeting, TranscriptSegment, MeetingStatus
from app.models.task import Task, TaskStatus, TaskPriority, DeadlineConfidence, ValidationStatus
from app.models.intelligence import Decision, Risk, IntelligenceRecord, IntelligenceType, DecisionStatus, RiskSeverity
from app.models.usage import AIUsageRecord, TaskCategory
from app.schemas.intelligence import (
    MeetingAnalysisResult,
    DecisionResponse,
    RiskResponse,
    SecondBrainResponse,
    CreativeSolutionsResponse,
    FlawDetectionResponse,
    ResearchBriefResponse
)
from app.ai.context_sieve import ContextSieve, SievePacket
from app.ai.evidence_validator import EvidenceValidator
from app.ai.token_budget import TokenBudgetManager
from app.ai.cache import AnalysisCache
from app.ai.meeting_state import MeetingStateManager
from app.ai.provider import qualcomm_client, QualcommInferenceError, QualcommAuthMissingError
from app.ai.model_router import QualcommModelRouter
from app.ai.demo_samples import DEMO_ANALYSIS_CACHE
from app.ai.research_service import ResearchService

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    """
    Sabha AI Unified Meeting Intelligence Pipeline.
    Shared identically across Live Meetings and Transcript Lab.
    Exclusively powered by Qualcomm Cloud AI Playground for LLM inference.
    """

    @classmethod
    async def analyze_meeting(
        cls,
        db: Session,
        meeting_id: str,
        workspace_id: str,
        depth: str = "full",  # "essential", "full", "full_research"
        force_recompute: bool = False
    ) -> MeetingAnalysisResult:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise ValueError(f"Meeting with id {meeting_id} not found.")

        # Update status
        meeting.status = MeetingStatus.ANALYZING
        db.commit()

        # Fetch transcript segments ordered by sequence
        raw_segments = (
            db.query(TranscriptSegment)
            .filter(TranscriptSegment.meeting_id == meeting_id, TranscriptSegment.is_deleted == False)
            .order_by(TranscriptSegment.sequence_number.asc())
            .all()
        )

        segment_dicts = [
            {
                "id": s.id,
                "sequence_number": s.sequence_number,
                "speaker_name": s.speaker_name,
                "text": s.text,
                "start_time": s.start_time,
                "end_time": s.end_time,
            }
            for s in raw_segments
        ]

        # 1. Run Context Sieve Preprocessing
        sieve_packet = ContextSieve.process(
            meeting_id=meeting_id,
            segments=segment_dicts,
            task_category="general",
            window_size=1
        )

        # Update meeting token metrics
        meeting.raw_token_count = sieve_packet.raw_token_count
        meeting.compressed_token_count = sieve_packet.compressed_token_count
        db.commit()

        # 2. Check Token Budget
        current_spent = 0.0  # Calculate from existing usage records if any
        budget_result = TokenBudgetManager.check_meeting_budget(
            current_meeting_spent_usd=current_spent,
            requested_depth=depth,
            max_budget_usd=settings.MAX_MEETING_BUDGET_USD
        )

        # 3. Cache check
        cache_key = AnalysisCache.generate_key(
            workspace_id=workspace_id,
            meeting_id=meeting_id,
            feature_name=f"analysis_{depth}",
            input_hash=sieve_packet.reproducible_hash,
            model_name=settings.QUALCOMM_ROUTINE_MODEL
        )
        if not force_recompute:
            cached_data = AnalysisCache.get(cache_key)
            if cached_data:
                meeting.status = MeetingStatus.ANALYZED
                db.commit()
                return MeetingAnalysisResult(**cached_data)

        # 4. Check whether Qualcomm Cloud AI is configured
        is_qualcomm_active = qualcomm_client.is_configured()

        if is_qualcomm_active:
            # Execute LIVE Qualcomm Cloud AI Inference
            result = await cls._execute_qualcomm_analysis(
                db=db,
                meeting=meeting,
                sieve_packet=sieve_packet,
                raw_segments=segment_dicts,
                depth=depth,
                budget_result=budget_result
            )
        else:
            # Qualcomm credentials not present: Handle honestly without fabricating
            result = await cls._execute_deterministic_or_demo_analysis(
                db=db,
                meeting=meeting,
                sieve_packet=sieve_packet,
                raw_segments=segment_dicts,
                depth=depth
            )

        # Cache result
        AnalysisCache.set(cache_key, result.dict())

        # Update meeting status
        meeting.status = MeetingStatus.ANALYZED
        db.commit()

        return result

    @classmethod
    async def _execute_qualcomm_analysis(
        cls,
        db: Session,
        meeting: Meeting,
        sieve_packet: SievePacket,
        raw_segments: List[Dict[str, Any]],
        depth: str,
        budget_result: Any
    ) -> MeetingAnalysisResult:
        """
        Executes real LLM analysis strictly using Qualcomm Cloud AI Playground.
        """
        # Route Routine Tasks -> Qualcomm Llama-3.1-8B
        routine_route = QualcommModelRouter.route_task(
            task_category="routine_extraction",
            estimated_tokens=sieve_packet.compressed_token_count
        )

        prompt = f"""You are the Sabha AI meeting intelligence engine running on Qualcomm Cloud AI.
Analyze this preprocessed transcript packet with provenance identifiers (<seg_id> Speaker: text).

Meeting Title: {meeting.title}
Meeting Date: {meeting.meeting_date.strftime('%Y-%m-%d %H:%M') if meeting.meeting_date else 'Unknown'}
Timezone: {meeting.timezone}
Project Context: {meeting.project_context or 'None provided'}

TRANSCRIPT PACKET:
{sieve_packet.context_text}

CRITICAL EXTRACTION RULES:
1. Never invent a task owner. If uncertain or unassigned, set assignee_name to null.
2. Never invent a deadline. If relative (e.g. 'Friday'), set deadline_text and resolve if meeting date is known.
3. Every task, decision, and risk MUST include an exact verbatim source_evidence_quote and source_segment_id.
4. Distinguish between 'I will do it' (commitment) and 'could someone do it?' (unassigned).
5. Preserve negations and withdrawn commitments.

Respond strictly with a JSON object matching this schema:
{{
  "executive_summary": "High level 2-4 sentence summary of discussions and outcomes.",
  "tasks": [
    {{
      "title": "Clear action title",
      "description": "Details",
      "assignee_name": "Name or null",
      "is_ownership_confirmed": true/false,
      "deadline_text": "e.g. by Friday or null",
      "deadline_confidence": "explicit" | "inferred" | "ambiguous" | "unspecified",
      "priority": "low" | "medium" | "high" | "urgent",
      "source_segment_id": "seg_id",
      "source_evidence_quote": "Verbatim quote from transcript"
    }}
  ],
  "decisions": [
    {{
      "title": "Decision title",
      "description": "Details of agreed choice",
      "status": "confirmed" | "proposed",
      "source_segment_id": "seg_id",
      "source_evidence_quote": "Verbatim quote"
    }}
  ],
  "risks": [
    {{
      "title": "Risk title",
      "description": "Concern details",
      "severity": "low" | "medium" | "high" | "critical",
      "potential_impact": "Impact",
      "suggested_mitigation": "Mitigation",
      "source_segment_id": "seg_id",
      "source_evidence_quote": "Verbatim quote"
    }}
  ]
}}"""

        # Execute routine extraction on Qualcomm
        routine_res = await qualcomm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a meeting analysis engine. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model=routine_route.selected_model,
            temperature=0.1,
            max_tokens=3000
        )

        # Record usage
        cls._record_usage(
            db=db,
            workspace_id=meeting.workspace_id,
            meeting_id=meeting.id,
            category=TaskCategory.ROUTINE_EXTRACTION,
            res=routine_res
        )

        # Parse routine output
        parsed_routine = cls._clean_and_parse_json(routine_res.content)
        summary = parsed_routine.get("executive_summary", "Meeting analyzed.")

        # Persist and validate tasks
        persisted_tasks: List[Task] = []
        for t_data in parsed_routine.get("tasks", []):
            v_res = EvidenceValidator.validate_task_claim(
                title=t_data.get("title", ""),
                assignee_name=t_data.get("assignee_name"),
                deadline_text=t_data.get("deadline_text"),
                source_quote=t_data.get("source_evidence_quote", ""),
                transcript_segments=raw_segments
            )
            task_obj = Task(
                meeting_id=meeting.id,
                workspace_id=meeting.workspace_id,
                title=t_data.get("title", "Untitled Task"),
                description=t_data.get("description"),
                assignee_name=t_data.get("assignee_name"),
                is_ownership_confirmed=t_data.get("is_ownership_confirmed", False) if t_data.get("assignee_name") else False,
                deadline_text=t_data.get("deadline_text"),
                deadline_confidence=DeadlineConfidence(t_data.get("deadline_confidence", "unspecified")),
                priority=TaskPriority(t_data.get("priority", "medium")),
                source_segment_id=v_res.matched_segment_id or t_data.get("source_segment_id"),
                source_evidence_quote=t_data.get("source_evidence_quote", ""),
                validation_status=v_res.status
            )
            db.add(task_obj)
            persisted_tasks.append(task_obj)

        # Persist and validate decisions
        persisted_decisions: List[Decision] = []
        for d_data in parsed_routine.get("decisions", []):
            v_res = EvidenceValidator.validate_decision_or_risk(
                title=d_data.get("title", ""),
                description=d_data.get("description", ""),
                source_quote=d_data.get("source_evidence_quote", ""),
                transcript_segments=raw_segments
            )
            dec_obj = Decision(
                meeting_id=meeting.id,
                workspace_id=meeting.workspace_id,
                title=d_data.get("title", "Decision"),
                description=d_data.get("description", ""),
                status=DecisionStatus(d_data.get("status", "confirmed")),
                source_evidence_quote=d_data.get("source_evidence_quote", ""),
                source_segment_id=v_res.matched_segment_id or d_data.get("source_segment_id"),
                validation_status=v_res.status
            )
            db.add(dec_obj)
            persisted_decisions.append(dec_obj)

        # Persist and validate risks
        persisted_risks: List[Risk] = []
        for r_data in parsed_routine.get("risks", []):
            v_res = EvidenceValidator.validate_decision_or_risk(
                title=r_data.get("title", ""),
                description=r_data.get("description", ""),
                source_quote=r_data.get("source_evidence_quote", ""),
                transcript_segments=raw_segments
            )
            risk_obj = Risk(
                meeting_id=meeting.id,
                workspace_id=meeting.workspace_id,
                title=r_data.get("title", "Identified Risk"),
                description=r_data.get("description", ""),
                severity=RiskSeverity(r_data.get("severity", "medium")),
                potential_impact=r_data.get("potential_impact"),
                suggested_mitigation=r_data.get("suggested_mitigation"),
                source_evidence_quote=r_data.get("source_evidence_quote", ""),
                source_segment_id=v_res.matched_segment_id or r_data.get("source_segment_id"),
                validation_status=v_res.status
            )
            db.add(risk_obj)
            persisted_risks.append(risk_obj)

        db.commit()

        # Execute Flagship Second Brain Review on Qualcomm 70B if requested
        second_brain_res = None
        if depth in ["full", "full_research"]:
            second_brain_res = await cls._execute_second_brain(
                db=db,
                meeting=meeting,
                sieve_packet=sieve_packet,
                raw_segments=raw_segments
            )

        # Execute Creative Solutions on Qualcomm Qwen-QwQ-32B if requested
        creative_res = None
        if depth in ["full", "full_research"]:
            creative_res = await cls._execute_creative_solutions(
                db=db,
                meeting=meeting,
                sieve_packet=sieve_packet
            )

        # Research brief
        research_briefs = []
        if depth == "full_research":
            brief = await ResearchService.generate_research_brief(
                question=f"Key technical challenge from {meeting.title}",
                context=meeting.project_context
            )
            research_briefs.append(brief)

        total_cost = routine_res.estimated_cost_usd

        return MeetingAnalysisResult(
            meeting_id=meeting.id,
            status="analyzed",
            executive_summary=summary,
            decisions=[DecisionResponse.from_orm(d) for d in persisted_decisions],
            risks=[RiskResponse.from_orm(r) for r in persisted_risks],
            second_brain=second_brain_res,
            creative_solutions=creative_res,
            research_briefs=research_briefs,
            tokens_raw=sieve_packet.raw_token_count,
            tokens_compressed=sieve_packet.compressed_token_count,
            compression_ratio=sieve_packet.compression_ratio,
            estimated_cost_usd=round(total_cost, 4),
            model_used=routine_res.model
        )

    @classmethod
    async def _execute_second_brain(
        cls,
        db: Session,
        meeting: Meeting,
        sieve_packet: SievePacket,
        raw_segments: List[Dict[str, Any]]
    ) -> SecondBrainResponse:
        """Runs Second Brain synthesis on Qualcomm Llama-3.3-70B."""
        route = QualcommModelRouter.route_task("second_brain")
        prompt = f"""You are the Sabha AI Second Brain synthesizer running on Qualcomm Cloud AI.
Analyze this meeting packet and deliver a 3-perspective intelligence synthesis:

TRANSCRIPT PACKET:
{sieve_packet.context_text}

PERSPECTIVES:
1. WHAT WE BELIEVE: Confirmed decisions, team assumptions, proposed plans, commitments, constraints.
2. WHAT WE MIGHT BE MISSING: Unsupported assumptions, contradictions, missing info, potential risks, inconsistent deadlines.
3. WHAT TO INVESTIGATE NEXT: Follow-up questions, small experiments, research topics, validation steps.

Respond strictly with valid JSON matching:
{{
  "what_we_believe": [
    {{"item": "Statement", "type": "decision"|"assumption"|"commitment"|"constraint", "evidence_quote": "Verbatim quote"}}
  ],
  "what_we_might_be_missing": [
    {{"finding": "Concern", "concern_type": "contradiction"|"unsupported_assumption"|"missing_info", "evidence_quote": "Verbatim quote", "reasoning": "Why it matters", "potential_impact": "Impact", "confidence": "high"|"medium", "suggested_verification": "How to verify"}}
  ],
  "what_to_investigate_next": [
    {{"recommendation": "Follow-up action", "action_type": "experiment"|"research"|"validation", "suggested_owner": "Name or null", "rationale": "Why"}}
  ]
}}"""

        res = await qualcomm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are the Second Brain synthesizer. Output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model=route.selected_model,
            temperature=0.2,
            max_tokens=2500
        )

        cls._record_usage(
            db=db,
            workspace_id=meeting.workspace_id,
            meeting_id=meeting.id,
            category=TaskCategory.COMPLEX_REASONING,
            res=res
        )

        parsed = cls._clean_and_parse_json(res.content)
        return SecondBrainResponse(
            what_we_believe=parsed.get("what_we_believe", []),
            what_we_might_be_missing=parsed.get("what_we_might_be_missing", []),
            what_to_investigate_next=parsed.get("what_to_investigate_next", []),
            model_name=res.model,
            pipeline_version="1.0.0"
        )

    @classmethod
    async def _execute_creative_solutions(
        cls,
        db: Session,
        meeting: Meeting,
        sieve_packet: SievePacket
    ) -> CreativeSolutionsResponse:
        """Runs Creative Solutions Engine on Qualcomm Qwen-QwQ-32B."""
        route = QualcommModelRouter.route_task("creative_solutions")
        prompt = f"""You are the Sabha AI Creative Solutions Engine running on Qualcomm Cloud AI.
Identify the primary technical/business bottleneck discussed in this transcript and propose 3 genuinely different architectural approaches:

TRANSCRIPT:
{sieve_packet.context_text}

Output strictly valid JSON:
{{
  "problem_statement": "Core bottleneck identified",
  "approaches": [
    {{
      "title": "Approach Title",
      "explanation": "Technical architecture explanation",
      "expected_benefits": ["Benefit 1", "Benefit 2"],
      "limitations": ["Limitation 1"],
      "required_resources": ["Resource 1"],
      "risks": ["Risk 1"],
      "assumptions": ["Assumption 1"],
      "suggested_experiments": ["Experiment 1"],
      "evaluation_criteria_scores": {{"feasibility": 8.0, "cost_efficiency": 9.0}}
    }}
  ]
}}"""

        res = await qualcomm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are the Creative Solutions Engine. Output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model=route.selected_model,
            temperature=0.3,
            max_tokens=2500
        )

        cls._record_usage(
            db=db,
            workspace_id=meeting.workspace_id,
            meeting_id=meeting.id,
            category=TaskCategory.CREATIVE,
            res=res
        )

        parsed = cls._clean_and_parse_json(res.content)
        return CreativeSolutionsResponse(
            problem_statement=parsed.get("problem_statement", "Bottleneck identified"),
            approaches=parsed.get("approaches", []),
            model_name=res.model
        )

    @classmethod
    async def _execute_deterministic_or_demo_analysis(
        cls,
        db: Session,
        meeting: Meeting,
        sieve_packet: SievePacket,
        raw_segments: List[Dict[str, Any]],
        depth: str
    ) -> MeetingAnalysisResult:
        """
        Honest offline fallback when QUALCOMM_API_KEY is not configured:
        - If matching sample scenario, loads verified demo dataset with explicit label.
        - If custom transcript, executes deterministic extraction via regex and Python/SQL rules.
        - NEVER calls another LLM provider!
        """
        # Check if matches sample scenario
        sample_key = None
        for k in ["sample_a", "sample_b", "sample_c"]:
            if k in meeting.title.lower() or (meeting.project_context and k in meeting.project_context.lower()):
                sample_key = k
                break

        if sample_key and sample_key in DEMO_ANALYSIS_CACHE:
            demo_data = DEMO_ANALYSIS_CACHE[sample_key]
            summary = f"[DEMO MODE] {demo_data['executive_summary']}"

            # Persist demo tasks
            persisted_tasks = []
            for t_data in demo_data.get("tasks", []):
                t_obj = Task(
                    meeting_id=meeting.id,
                    workspace_id=meeting.workspace_id,
                    title=t_data["title"],
                    assignee_name=t_data.get("assignee_name"),
                    is_ownership_confirmed=t_data.get("is_ownership_confirmed", False),
                    deadline_text=t_data.get("deadline_text"),
                    deadline_confidence=DeadlineConfidence(t_data.get("deadline_confidence", "unspecified")),
                    priority=TaskPriority(t_data.get("priority", "medium")),
                    status=TaskStatus(t_data.get("status", "pending")),
                    blocker_reason=t_data.get("blocker_reason"),
                    source_evidence_quote=t_data.get("source_evidence_quote", ""),
                    validation_status=ValidationStatus(t_data.get("validation_status", "evidence_supported"))
                )
                db.add(t_obj)
                persisted_tasks.append(t_obj)

            # Persist demo decisions
            persisted_decisions = []
            for d_data in demo_data.get("decisions", []):
                d_obj = Decision(
                    meeting_id=meeting.id,
                    workspace_id=meeting.workspace_id,
                    title=d_data["title"],
                    description=d_data["description"],
                    status=DecisionStatus(d_data.get("status", "confirmed")),
                    source_evidence_quote=d_data["source_evidence_quote"],
                    validation_status=ValidationStatus.EVIDENCE_SUPPORTED
                )
                db.add(d_obj)
                persisted_decisions.append(d_obj)

            # Persist demo risks
            persisted_risks = []
            for r_data in demo_data.get("risks", []):
                r_obj = Risk(
                    meeting_id=meeting.id,
                    workspace_id=meeting.workspace_id,
                    title=r_data["title"],
                    description=r_data["description"],
                    severity=RiskSeverity(r_data.get("severity", "medium")),
                    potential_impact=r_data.get("potential_impact"),
                    suggested_mitigation=r_data.get("suggested_mitigation"),
                    source_evidence_quote=r_data["source_evidence_quote"],
                    validation_status=ValidationStatus.EVIDENCE_SUPPORTED
                )
                db.add(r_obj)
                persisted_risks.append(r_obj)

            db.commit()

            sb_data = demo_data.get("second_brain")
            sb_response = None
            if sb_data and depth in ["full", "full_research"]:
                sb_response = SecondBrainResponse(
                    what_we_believe=sb_data.get("what_we_believe", []),
                    what_we_might_be_missing=sb_data.get("what_we_might_be_missing", []),
                    what_to_investigate_next=sb_data.get("what_to_investigate_next", []),
                    model_name="deterministic_demo_pipeline [QUALCOMM_API_KEY NOT CONFIGURED]",
                    pipeline_version="1.0.0"
                )

            cs_data = demo_data.get("creative_solutions")
            cs_response = None
            if cs_data and depth in ["full", "full_research"]:
                cs_response = CreativeSolutionsResponse(
                    problem_statement=cs_data["problem_statement"],
                    approaches=cs_data["approaches"],
                    model_name="deterministic_demo_pipeline [QUALCOMM_API_KEY NOT CONFIGURED]"
                )

            return MeetingAnalysisResult(
                meeting_id=meeting.id,
                status="analyzed",
                executive_summary=summary,
                decisions=[DecisionResponse.from_orm(d) for d in persisted_decisions],
                risks=[RiskResponse.from_orm(r) for r in persisted_risks],
                second_brain=sb_response,
                creative_solutions=cs_response,
                research_briefs=[],
                tokens_raw=sieve_packet.raw_token_count,
                tokens_compressed=sieve_packet.compressed_token_count,
                compression_ratio=sieve_packet.compression_ratio,
                estimated_cost_usd=0.0,
                model_used="deterministic_demo_pipeline [DEMO MODE - NO LIVE INFERENCE CLAIMED]"
            )

        # Custom transcript with missing Qualcomm credentials -> Deterministic Rule Engine
        summary = (
            f"[OFFLINE DETERMINISTIC EXTRACTION] Analyzed {len(raw_segments)} segments. "
            f"QUALCOMM_API_KEY is not configured in environment. "
            f"Rule-based deterministic engine detected potential action items and decisions without live LLM inference."
        )

        detected_tasks = []
        detected_decisions = []
        detected_risks = []

        for seg in sieve_packet.included_segments:
            text = seg.text
            # Task rule
            if ContextSieve.TASK_CUES.search(text):
                assignee = seg.speaker_name if any(p in text.lower() for p in ["i will", "i'll", "i can"]) else None
                t_obj = Task(
                    meeting_id=meeting.id,
                    workspace_id=meeting.workspace_id,
                    title=f"Action item from {seg.speaker_name or 'participant'}: {text[:80]}...",
                    assignee_name=assignee,
                    is_ownership_confirmed=bool(assignee),
                    deadline_text="Extracted from cues" if ContextSieve.DATE_AND_DEADLINE_CUES.search(text) else None,
                    deadline_confidence=DeadlineConfidence.AMBIGUOUS if ContextSieve.DATE_AND_DEADLINE_CUES.search(text) else DeadlineConfidence.UNSPECIFIED,
                    priority=TaskPriority.MEDIUM,
                    source_segment_id=seg.id,
                    source_evidence_quote=text,
                    validation_status=ValidationStatus.EVIDENCE_SUPPORTED
                )
                db.add(t_obj)
                detected_tasks.append(t_obj)

            # Decision rule
            if ContextSieve.DECISION_CUES.search(text):
                d_obj = Decision(
                    meeting_id=meeting.id,
                    workspace_id=meeting.workspace_id,
                    title=f"Agreed item: {text[:60]}...",
                    description=text,
                    status=DecisionStatus.CONFIRMED,
                    source_evidence_quote=text,
                    source_segment_id=seg.id,
                    validation_status=ValidationStatus.EVIDENCE_SUPPORTED
                )
                db.add(d_obj)
                detected_decisions.append(d_obj)

            # Risk rule
            if ContextSieve.RISK_AND_BLOCKER_CUES.search(text):
                r_obj = Risk(
                    meeting_id=meeting.id,
                    workspace_id=meeting.workspace_id,
                    title=f"Potential risk: {text[:60]}...",
                    description=text,
                    severity=RiskSeverity.HIGH if "critical" in text.lower() or "block" in text.lower() else RiskSeverity.MEDIUM,
                    source_evidence_quote=text,
                    source_segment_id=seg.id,
                    validation_status=ValidationStatus.EVIDENCE_SUPPORTED
                )
                db.add(r_obj)
                detected_risks.append(r_obj)

        db.commit()

        return MeetingAnalysisResult(
            meeting_id=meeting.id,
            status="analyzed",
            executive_summary=summary,
            decisions=[DecisionResponse.from_orm(d) for d in detected_decisions],
            risks=[RiskResponse.from_orm(r) for r in detected_risks],
            second_brain=None,
            creative_solutions=None,
            research_briefs=[],
            tokens_raw=sieve_packet.raw_token_count,
            tokens_compressed=sieve_packet.compressed_token_count,
            compression_ratio=sieve_packet.compression_ratio,
            estimated_cost_usd=0.0,
            model_used="deterministic_python_rule_engine [QUALCOMM_API_KEY OFFLINE]"
        )

    @classmethod
    def _clean_and_parse_json(cls, raw: str) -> Dict[str, Any]:
        raw = raw.strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            if len(parts) >= 2:
                raw = parts[1]
                if raw.startswith("json"):
                    raw = raw[4:]
        raw = raw.strip()
        return json.loads(raw)

    @classmethod
    def _record_usage(
        cls,
        db: Session,
        workspace_id: str,
        meeting_id: str,
        category: TaskCategory,
        res: Any
    ):
        usage = AIUsageRecord(
            workspace_id=workspace_id,
            meeting_id=meeting_id,
            task_category=category,
            provider="qualcomm_cloud_ai",
            model=res.model,
            input_tokens=res.input_tokens,
            output_tokens=res.output_tokens,
            is_measured=res.is_measured,
            estimated_cost_usd=res.estimated_cost_usd,
            latency_ms=res.latency_ms,
            validation_passed=True
        )
        db.add(usage)
        db.commit()

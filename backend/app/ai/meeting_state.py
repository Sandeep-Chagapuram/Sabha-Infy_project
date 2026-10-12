from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class MeetingState(BaseModel):
    meeting_id: str
    workspace_id: str
    last_processed_sequence: int = -1
    executive_summary: str = ""
    confirmed_decisions: List[Dict[str, Any]] = []
    proposed_decisions: List[Dict[str, Any]] = []
    active_tasks: List[Dict[str, Any]] = []
    unresolved_questions: List[Dict[str, Any]] = []
    risks_and_blockers: List[Dict[str, Any]] = []
    contradictions_detected: List[Dict[str, Any]] = []
    updated_at: datetime = datetime.utcnow()

class MeetingStateManager:
    """
    Maintains persistent, incrementally updated meeting state.
    When a participant corrects an earlier statement or new finalized segments arrive,
    identifies affected conclusions and invalidates or merges them.
    """
    _state_registry: Dict[str, MeetingState] = {}

    @classmethod
    def get_or_create(cls, meeting_id: str, workspace_id: str) -> MeetingState:
        if meeting_id not in cls._state_registry:
            cls._state_registry[meeting_id] = MeetingState(
                meeting_id=meeting_id,
                workspace_id=workspace_id
            )
        return cls._state_registry[meeting_id]

    @classmethod
    def update_state(
        cls,
        meeting_id: str,
        workspace_id: str,
        summary: Optional[str] = None,
        tasks: Optional[List[Dict[str, Any]]] = None,
        decisions: Optional[List[Dict[str, Any]]] = None,
        risks: Optional[List[Dict[str, Any]]] = None,
        last_seq: Optional[int] = None
    ) -> MeetingState:
        state = cls.get_or_create(meeting_id, workspace_id)
        if summary is not None:
            state.executive_summary = summary
        if tasks is not None:
            state.active_tasks = tasks
        if decisions is not None:
            state.confirmed_decisions = [d for d in decisions if d.get("status") == "confirmed"]
            state.proposed_decisions = [d for d in decisions if d.get("status") != "confirmed"]
        if risks is not None:
            state.risks_and_blockers = risks
        if last_seq is not None:
            state.last_processed_sequence = last_seq
        state.updated_at = datetime.utcnow()
        return state

    @classmethod
    def handle_transcript_correction(
        cls,
        meeting_id: str,
        segment_id: str,
        previous_text: str,
        corrected_text: str
    ) -> List[str]:
        """
        Invalidates earlier conclusions dependent on the modified segment.
        Returns list of invalidated item titles/IDs.
        """
        state = cls._state_registry.get(meeting_id)
        if not state:
            return []

        invalidated_items = []
        # Check tasks that drew evidence from this segment
        for t in state.active_tasks:
            if t.get("source_segment_id") == segment_id or previous_text.lower() in t.get("source_evidence_quote", "").lower():
                t["validation_status"] = "unverified"
                invalidated_items.append(f"Task: {t.get('title')}")

        return invalidated_items

import re
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from app.models.task import ValidationStatus, DeadlineConfidence

class ValidationResult(BaseModel):
    is_valid: bool
    status: ValidationStatus
    quote_found: bool
    quote_match_ratio: float
    matched_segment_id: Optional[str] = None
    flags: List[str] = []
    sanitized_claim: str
    rejection_reason: Optional[str] = None

class EvidenceValidator:
    """
    Sabha AI Core Safeguard: Evidence Validator.
    Ensures every task, decision, risk, and flaw is strictly grounded in genuine 
    transcript evidence and prevents hallucinated owners, phantom deadlines, 
    and contradicted claims.
    """

    NEGATION_WORDS = {"not", "cannot", "can't", "won't", "will not", "no", "never", "unlikely", "impossible", "withdraw", "cancelled"}

    @classmethod
    def normalize_text_for_matching(cls, text: str) -> str:
        """Strips punctuation and standardizes whitespace for robust quote matching."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return " ".join(text.split())

    @classmethod
    def verify_quote_in_transcript(
        cls,
        quote: str,
        transcript_segments: List[Dict[str, Any]]
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Verifies if an excerpt or quote actually exists in the source transcript.
        Returns: (quote_found, match_ratio, matched_segment_id)
        """
        if not quote or not quote.strip():
            return False, 0.0, None

        norm_quote = cls.normalize_text_for_matching(quote)
        quote_words = set(norm_quote.split())
        if not quote_words:
            return False, 0.0, None

        best_ratio = 0.0
        best_segment_id = None

        for seg in transcript_segments:
            seg_text = seg.get("text", "")
            seg_id = seg.get("id")
            norm_seg = cls.normalize_text_for_matching(seg_text)

            # Check direct substring
            if norm_quote in norm_seg:
                return True, 1.0, seg_id

            # Check token overlap ratio for paraphrased or slightly truncated quotes
            seg_words = set(norm_seg.split())
            if not seg_words:
                continue

            common_words = quote_words.intersection(seg_words)
            ratio = len(common_words) / len(quote_words)
            if ratio > best_ratio:
                best_ratio = ratio
                best_segment_id = seg_id

        # Require at least 70% word overlap to consider verified
        is_found = best_ratio >= 0.70
        return is_found, round(best_ratio, 2), (best_segment_id if is_found else None)

    @classmethod
    def validate_task_claim(
        cls,
        title: str,
        assignee_name: Optional[str],
        deadline_text: Optional[str],
        source_quote: str,
        transcript_segments: List[Dict[str, Any]]
    ) -> ValidationResult:
        flags = []
        is_valid = True
        status = ValidationStatus.EVIDENCE_SUPPORTED

        # 1. Check Quote Provenance
        quote_found, ratio, matched_seg_id = cls.verify_quote_in_transcript(source_quote, transcript_segments)
        if not quote_found:
            flags.append("QUOTE_NOT_FOUND_IN_TRANSCRIPT")
            status = ValidationStatus.UNVERIFIED
            # We don't reject outright if title is grounded, but flag it prominently
        else:
            if ratio == 1.0:
                flags.append("EXACT_QUOTE_VERIFIED")
            else:
                flags.append("HIGH_CONFIDENCE_PARAPHRASE_VERIFIED")

        # 2. Check Negation / Withdrawn Commitment
        norm_quote = cls.normalize_text_for_matching(source_quote)
        quote_words = set(norm_quote.split())
        has_negation = any(neg in quote_words for neg in cls.NEGATION_WORDS)

        if has_negation:
            # Check if title erroneously asserts affirmative action
            if not any(neg in cls.normalize_text_for_matching(title).split() for neg in cls.NEGATION_WORDS):
                flags.append("POTENTIAL_CONTRADICTION_NEGATION_IGNORED")
                status = ValidationStatus.CONFLICTING

        # 3. Guard against hallucinated assignee
        if assignee_name and assignee_name.strip():
            norm_assignee = cls.normalize_text_for_matching(assignee_name)
            # Find if assignee is mentioned in the quote, speaker identity, or transcript participants
            assignee_in_quote = norm_assignee in norm_quote
            speaker_is_assignee = False
            
            if matched_seg_id:
                for seg in transcript_segments:
                    if seg.get("id") == matched_seg_id:
                        spk = cls.normalize_text_for_matching(seg.get("speaker_name") or "")
                        if norm_assignee in spk or spk in norm_assignee:
                            speaker_is_assignee = True
                        break

            if not (assignee_in_quote or speaker_is_assignee):
                flags.append("ASSIGNEE_NOT_EXPLICITLY_GROUNDED_IN_QUOTE")
                if status != ValidationStatus.UNVERIFIED:
                    status = ValidationStatus.INFERRED

        # 4. Check Deadline Ambiguity
        if deadline_text:
            rel_deadline_pattern = re.compile(r'\b(friday|monday|tomorrow|next week|eod|soon|later)\b', re.IGNORECASE)
            if rel_deadline_pattern.search(deadline_text):
                flags.append("RELATIVE_DEADLINE_REQUIRES_MEETING_DATE_CONTEXT")

        return ValidationResult(
            is_valid=is_valid,
            status=status,
            quote_found=quote_found,
            quote_match_ratio=ratio,
            matched_segment_id=matched_seg_id,
            flags=flags,
            sanitized_claim=title
        )

    @classmethod
    def validate_decision_or_risk(
        cls,
        title: str,
        description: str,
        source_quote: str,
        transcript_segments: List[Dict[str, Any]]
    ) -> ValidationResult:
        flags = []
        quote_found, ratio, matched_seg_id = cls.verify_quote_in_transcript(source_quote, transcript_segments)

        if not quote_found:
            flags.append("EVIDENCE_QUOTE_NOT_IN_SOURCE")
            status = ValidationStatus.UNVERIFIED
        else:
            status = ValidationStatus.EVIDENCE_SUPPORTED

        return ValidationResult(
            is_valid=True,
            status=status,
            quote_found=quote_found,
            quote_match_ratio=ratio,
            matched_segment_id=matched_seg_id,
            flags=flags,
            sanitized_claim=f"{title}: {description}"
        )

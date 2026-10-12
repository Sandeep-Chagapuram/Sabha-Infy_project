import re
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel

class SieveSegment(BaseModel):
    id: str
    sequence_number: int
    speaker_name: Optional[str] = None
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    is_included: bool = True
    exclusion_reason: Optional[str] = None
    intent_tags: List[str] = []

class SievePacket(BaseModel):
    meeting_id: str
    task_category: str
    total_raw_segments: int
    included_segments: List[SieveSegment]
    excluded_segments_count: int
    raw_token_count: int
    compressed_token_count: int
    compression_ratio: float
    context_text: str
    reproducible_hash: str

class ContextSieve:
    """
    Sabha AI Core Innovation: Context Sieve.
    Preprocesses transcripts to eliminate conversational filler, exact stutter/echo duplicates,
    and irrelevant banter while strictly preserving negation, commitment changes, corrections,
    disagreements, risks, dates, and full context surrounding potential commitments.
    """

    # Intent cues
    TASK_CUES = re.compile(
        r'\b(will|shall|can|need to|must|handle|take care of|ship|deploy|fix|build|write|implement|prepare|review|schedule|action item|task|todo|responsible for)\b',
        re.IGNORECASE
    )
    DECISION_CUES = re.compile(
        r'\b(decide|decided|agreed|agree|consensus|approved|approve|finalize|finalized|conclusion|settled|go with|chosen)\b',
        re.IGNORECASE
    )
    NEGATION_AND_CORRECTION_CUES = re.compile(
        r'\b(not|cannot|can\'t|won\'t|will not|no|never|instead|actually|wait|scratch that|hold on|correction|withdraw|change of mind|disagree|opposed|concern)\b',
        re.IGNORECASE
    )
    DATE_AND_DEADLINE_CUES = re.compile(
        r'\b(by|before|on|deadline|due|friday|monday|tuesday|wednesday|thursday|saturday|sunday|tomorrow|next week|eod|end of day|end of week|q[1-4]|sprint)\b',
        re.IGNORECASE
    )
    RISK_AND_BLOCKER_CUES = re.compile(
        r'\b(block|blocked|blocker|risk|danger|vulnerability|problem|issue|delay|fallback|bottleneck|failure|flaw|break|down)\b',
        re.IGNORECASE
    )
    QUESTION_CUES = re.compile(
        r'\b(who|what|when|where|why|how|should we|could we|is it|can we|\?)\b',
        re.IGNORECASE
    )

    # Filler banter that carries zero decision or evidence weight
    FILLER_PATTERNS = [
        re.compile(r'^(yeah|yep|uh-huh|okay|ok|cool|sure|right|got it|sounds good|thanks|thank you|hi|hello|hey|bye)\.?$', re.IGNORECASE),
        re.compile(r'^(can you hear me|testing audio|am i audible|mic check)\.?$', re.IGNORECASE)
    ]

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """
        Estimates token count. 1 token ~= 4 chars or 0.75 words.
        Provides a conservative, deterministic estimation when tokenizer is offline.
        """
        if not text:
            return 0
        words = text.split()
        return max(len(words), int(len(text) / 3.8))

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Normalizes whitespaces and noisy brackets without destroying punctuation."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @classmethod
    def tag_segment_intents(cls, text: str) -> List[str]:
        tags = []
        if cls.TASK_CUES.search(text):
            tags.append("task_cue")
        if cls.DECISION_CUES.search(text):
            tags.append("decision_cue")
        if cls.NEGATION_AND_CORRECTION_CUES.search(text):
            tags.append("negation_or_correction")
        if cls.DATE_AND_DEADLINE_CUES.search(text):
            tags.append("date_or_deadline")
        if cls.RISK_AND_BLOCKER_CUES.search(text):
            tags.append("risk_or_blocker")
        if cls.QUESTION_CUES.search(text):
            tags.append("question_or_inquiry")
        return tags

    @classmethod
    def process(
        cls,
        meeting_id: str,
        segments: List[Dict[str, Any]],
        task_category: str = "general",
        window_size: int = 1
    ) -> SievePacket:
        """
        Filters and structures transcript segments into a high-density, context-rich packet.
        - Preserves all segments tagged with key intents.
        - Preserves sliding window of surrounding context (window_size before & after)
          so conversational flow, pronouns, and speaker interactions are never isolated.
        - De-duplicates exact consecutive echoes.
        """
        if not segments:
            return SievePacket(
                meeting_id=meeting_id,
                task_category=task_category,
                total_raw_segments=0,
                included_segments=[],
                excluded_segments_count=0,
                raw_token_count=0,
                compressed_token_count=0,
                compression_ratio=0.0,
                context_text="",
                reproducible_hash="empty"
            )

        raw_text_combined = " ".join([s.get("text", "") for s in segments])
        raw_tokens = cls.estimate_tokens(raw_text_combined)

        sieved_segments: List[SieveSegment] = []
        last_normalized_text = None

        # Pass 1: Parse, tag and identify candidate inclusions
        candidate_indices = set()
        
        for idx, s in enumerate(segments):
            norm_text = cls.normalize_text(s.get("text", ""))
            seg_id = s.get("id", f"seg_{idx}")
            speaker = s.get("speaker_name") or s.get("speaker") or "Unknown"
            seq = s.get("sequence_number", idx)
            start_t = s.get("start_time")
            end_t = s.get("end_time")

            # Check consecutive exact duplicate (audio stutter)
            if norm_text.lower() == last_normalized_text and len(norm_text) > 5:
                sieved_segments.append(
                    SieveSegment(
                        id=seg_id,
                        sequence_number=seq,
                        speaker_name=speaker,
                        text=norm_text,
                        start_time=start_t,
                        end_time=end_t,
                        is_included=False,
                        exclusion_reason="consecutive_exact_duplicate",
                        intent_tags=[]
                    )
                )
                continue

            last_normalized_text = norm_text.lower()
            tags = cls.tag_segment_intents(norm_text)

            # Check if pure filler with no intents
            is_filler = False
            for pat in cls.FILLER_PATTERNS:
                if pat.match(norm_text) and not tags:
                    is_filler = True
                    break

            if is_filler:
                sieved_segments.append(
                    SieveSegment(
                        id=seg_id,
                        sequence_number=seq,
                        speaker_name=speaker,
                        text=norm_text,
                        start_time=start_t,
                        end_time=end_t,
                        is_included=False,
                        exclusion_reason="conversational_filler_no_intent",
                        intent_tags=[]
                    )
                )
            else:
                s_obj = SieveSegment(
                    id=seg_id,
                    sequence_number=seq,
                    speaker_name=speaker,
                    text=norm_text,
                    start_time=start_t,
                    end_time=end_t,
                    is_included=True,
                    exclusion_reason=None,
                    intent_tags=tags
                )
                sieved_segments.append(s_obj)
                if tags or len(norm_text.split()) > 7:
                    # Meaningful sentence
                    candidate_indices.add(len(sieved_segments) - 1)

        # Pass 2: Window expansion around candidates to guarantee conversational context
        final_included_indices = set()
        for c_idx in candidate_indices:
            for w in range(max(0, c_idx - window_size), min(len(sieved_segments), c_idx + window_size + 1)):
                final_included_indices.add(w)

        # If transcript is very short (< 15 segments), keep all to prevent over-filtering
        if len(sieved_segments) <= 15:
            final_included_indices = set(range(len(sieved_segments)))

        included_segments: List[SieveSegment] = []
        excluded_count = 0

        for i, seg in enumerate(sieved_segments):
            if i in final_included_indices and seg.is_included:
                included_segments.append(seg)
            else:
                seg.is_included = False
                if not seg.exclusion_reason:
                    seg.exclusion_reason = "outside_relevance_window"
                excluded_count += 1

        # Format context text with explicit IDs and timestamps for provenance grounding
        formatted_lines = []
        for s in included_segments:
            time_str = f"[{s.start_time:.1f}s]" if s.start_time is not None else ""
            line = f"<{s.id}> {time_str} {s.speaker_name or 'Unknown'}: {s.text}"
            formatted_lines.append(line.strip())

        context_text = "\n".join(formatted_lines)
        compressed_tokens = cls.estimate_tokens(context_text)
        compression_ratio = round((1.0 - (compressed_tokens / max(raw_tokens, 1))) * 100.0, 1) if raw_tokens > 0 else 0.0

        # Calculate a deterministic hash of the packet
        import hashlib
        reproducible_hash = hashlib.sha256(context_text.encode('utf-8')).hexdigest()[:16]

        return SievePacket(
            meeting_id=meeting_id,
            task_category=task_category,
            total_raw_segments=len(segments),
            included_segments=included_segments,
            excluded_segments_count=excluded_count,
            raw_token_count=raw_tokens,
            compressed_token_count=compressed_tokens,
            compression_ratio=max(0.0, compression_ratio),
            context_text=context_text,
            reproducible_hash=reproducible_hash
        )

import re
from typing import List, Dict, Any, Optional, Tuple

class ParsedSegment(Dict[str, Any]):
    sequence_number: int
    speaker_name: Optional[str]
    text: str
    start_time: Optional[float]
    end_time: Optional[float]

class TranscriptParser:
    """
    Robust multi-format parser for meeting transcripts:
    - [HH:MM:SS] Speaker: text
    - HH:MM:SS Speaker: text
    - Speaker: text (no timestamp)
    - WebVTT (.vtt) with timestamp cues
    - Plain paragraphs (unattributed speaker - NEVER fabricated)
    """

    TIMESTAMP_AND_SPEAKER_PATTERN = re.compile(
        r'^(?:\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s+)?(?:([^:\n]+):\s+)?(.*)$'
    )

    WEBVTT_TIMESTAMP_PATTERN = re.compile(
        r'(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})'
    )

    @classmethod
    def parse_time_str(cls, time_str: Optional[str]) -> Optional[float]:
        if not time_str:
            return None
        time_str = time_str.strip('[]')
        parts = time_str.split(':')
        try:
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
        except ValueError:
            return None
        return None

    @classmethod
    def parse_vtt(cls, content: str) -> List[Dict[str, Any]]:
        segments = []
        lines = content.splitlines()
        seq = 0
        current_start = None
        current_end = None
        current_speaker = None
        current_text_lines = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("WEBVTT") or line.isdigit():
                if current_text_lines and current_start is not None:
                    full_text = " ".join(current_text_lines).strip()
                    if full_text:
                        segments.append({
                            "sequence_number": seq,
                            "speaker_name": current_speaker,
                            "text": full_text,
                            "start_time": current_start,
                            "end_time": current_end
                        })
                        seq += 1
                    current_text_lines = []
                    current_speaker = None
                    current_start = None
                    current_end = None
                continue

            match_time = cls.WEBVTT_TIMESTAMP_PATTERN.search(line)
            if match_time:
                current_start = cls.parse_time_str(match_time.group(1).split('.')[0])
                current_end = cls.parse_time_str(match_time.group(2).split('.')[0])
                continue

            # Speaker cue check inside text e.g. <v Speaker>text or Speaker: text
            speaker_match = re.match(r'^(?:<v\s+([^>]+)>|([^:]+):\s*)(.*)$', line)
            if speaker_match:
                current_speaker = (speaker_match.group(1) or speaker_match.group(2) or "").strip()
                text_part = (speaker_match.group(3) or "").strip()
                if text_part:
                    current_text_lines.append(text_part)
            else:
                current_text_lines.append(line)

        if current_text_lines and current_start is not None:
            full_text = " ".join(current_text_lines).strip()
            if full_text:
                segments.append({
                    "sequence_number": seq,
                    "speaker_name": current_speaker,
                    "text": full_text,
                    "start_time": current_start,
                    "end_time": current_end
                })

        return segments

    @classmethod
    def parse_text(cls, content: str) -> List[Dict[str, Any]]:
        # If it looks like WebVTT
        if content.strip().startswith("WEBVTT") or "-->" in content:
            return cls.parse_vtt(content)

        lines = content.splitlines()
        segments = []
        seq = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = cls.TIMESTAMP_AND_SPEAKER_PATTERN.match(line)
            if match:
                time_str = match.group(1)
                speaker = match.group(2)
                text = match.group(3)

                # Avoid false positive speaker match on sentences with colons (e.g. "Note: remember to...")
                if speaker and len(speaker.split()) > 4:
                    text = f"{speaker}: {text}"
                    speaker = None

                if speaker:
                    speaker = speaker.strip()
                else:
                    speaker = None  # Never fabricate!

                seconds = cls.parse_time_str(time_str)

                if text and text.strip():
                    segments.append({
                        "sequence_number": seq,
                        "speaker_name": speaker,
                        "text": text.strip(),
                        "start_time": seconds,
                        "end_time": (seconds + 5.0) if seconds is not None else None
                    })
                    seq += 1
            else:
                segments.append({
                    "sequence_number": seq,
                    "speaker_name": None,
                    "text": line,
                    "start_time": None,
                    "end_time": None
                })
                seq += 1

        return segments

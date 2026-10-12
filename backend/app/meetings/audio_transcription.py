import os
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.config import settings

class AudioTranscriptResult(BaseModel):
    is_success: bool
    segments: List[Dict[str, Any]]
    raw_text: str
    duration_seconds: Optional[float] = None
    provider: str
    message: Optional[str] = None

class AudioTranscriptionService:
    """
    Speech-to-Text (STT) Service.
    Strictly separate from Qualcomm Cloud AI LLM inference.
    Supports integration with dedicated ASR / Speech-to-Text endpoints (e.g. Whisper API or local server).
    If no STT endpoint is configured, returns an honest diagnostic notice.
    """

    ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac"}
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit

    @classmethod
    def is_stt_configured(cls) -> bool:
        stt_key = os.getenv("STT_API_KEY")
        stt_endpoint = os.getenv("STT_ENDPOINT")
        return bool(stt_key or stt_endpoint)

    @classmethod
    def validate_file(cls, filename: str, file_size: int) -> Optional[str]:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            return f"Unsupported audio format '{ext}'. Allowed formats: {', '.join(cls.ALLOWED_EXTENSIONS)}"
        if file_size > cls.MAX_FILE_SIZE_BYTES:
            return f"Audio file size exceeds maximum limit of 50 MB ({file_size / (1024*1024):.1f} MB provided)."
        return None

    @classmethod
    async def transcribe_audio_file(
        cls,
        file_bytes: bytes,
        filename: str
    ) -> AudioTranscriptResult:
        validation_error = cls.validate_file(filename, len(file_bytes))
        if validation_error:
            return AudioTranscriptResult(
                is_success=False,
                segments=[],
                raw_text="",
                provider="none",
                message=validation_error
            )

        stt_endpoint = os.getenv("STT_ENDPOINT")
        stt_key = os.getenv("STT_API_KEY")

        if not (stt_endpoint or stt_key):
            # Honest diagnostic notice
            return AudioTranscriptResult(
                is_success=False,
                segments=[],
                raw_text="",
                provider="unconfigured",
                message=(
                    "Dedicated Speech-to-Text (STT) service is not configured in .env (STT_ENDPOINT or STT_API_KEY). "
                    "Note: LLM inference is powered exclusively by Qualcomm Cloud AI Playground, but audio transcription "
                    "requires an active ASR/Whisper endpoint. Please paste or upload a .txt/.md/.vtt transcript instead."
                )
            )

        # If endpoint is configured, dispatch audio request
        try:
            url = stt_endpoint or "https://api.openai.com/v1/audio/transcriptions"
            headers = {}
            if stt_key:
                headers["Authorization"] = f"Bearer {stt_key}"

            files = {"file": (filename, file_bytes, "audio/mpeg")}
            data = {"model": "whisper-1", "response_format": "verbose_json"}

            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, files=files, data=data)

            if resp.status_code != 200:
                return AudioTranscriptResult(
                    is_success=False,
                    segments=[],
                    raw_text="",
                    provider="custom_stt",
                    message=f"STT provider returned error HTTP {resp.status_code}: {resp.text}"
                )

            res_json = resp.json()
            raw_text = res_json.get("text", "")
            raw_segments = res_json.get("segments", [])

            parsed_segments = []
            for idx, seg in enumerate(raw_segments):
                parsed_segments.append({
                    "sequence_number": idx,
                    "speaker_name": None,  # Diarization absent in standard ASR; preserved as Unknown
                    "text": seg.get("text", "").strip(),
                    "start_time": seg.get("start"),
                    "end_time": seg.get("end")
                })

            return AudioTranscriptResult(
                is_success=True,
                segments=parsed_segments,
                raw_text=raw_text,
                duration_seconds=res_json.get("duration"),
                provider="configured_asr",
                message="Audio transcribed successfully."
            )

        except Exception as e:
            return AudioTranscriptResult(
                is_success=False,
                segments=[],
                raw_text="",
                provider="error",
                message=f"Failed to transcribe audio file: {str(e)}"
            )

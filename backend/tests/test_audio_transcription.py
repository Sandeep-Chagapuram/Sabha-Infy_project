import pytest
from app.meetings.audio_transcription import AudioTranscriptionService

def test_validate_audio_file_formats():
    assert AudioTranscriptionService.validate_file("meeting.mp3", 1000) is None
    assert AudioTranscriptionService.validate_file("recording.wav", 1000) is None
    assert AudioTranscriptionService.validate_file("session.m4a", 1000) is None
    
    # Unsupported formats
    err = AudioTranscriptionService.validate_file("document.pdf", 1000)
    assert err is not None
    assert "Unsupported audio format" in err

def test_validate_audio_file_size_limit():
    large_size = 55 * 1024 * 1024  # 55 MB exceeds 50 MB
    err = AudioTranscriptionService.validate_file("huge.wav", large_size)
    assert err is not None
    assert "exceeds maximum limit" in err

@pytest.mark.asyncio
async def test_transcribe_audio_unconfigured_honest_notice():
    # When STT_API_KEY / STT_ENDPOINT are not set
    result = await AudioTranscriptionService.transcribe_audio_file(
        file_bytes=b"fake audio data",
        filename="test.mp3"
    )
    assert result.is_success is False
    assert result.provider == "unconfigured"
    assert "Dedicated Speech-to-Text (STT) service is not configured" in (result.message or "")
    assert "Qualcomm Cloud AI" in (result.message or "")

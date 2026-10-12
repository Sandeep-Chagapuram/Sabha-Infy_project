import pytest
from app.meetings.transcript_parser import TranscriptParser

def test_parse_bracketed_timestamp_and_speaker():
    raw = "[00:01:15] Priya: We need to finish the API integration by Friday."
    segments = TranscriptParser.parse_text(raw)
    assert len(segments) == 1
    assert segments[0]["speaker_name"] == "Priya"
    assert segments[0]["start_time"] == 75.0
    assert segments[0]["text"] == "We need to finish the API integration by Friday."

def test_parse_unbracketed_timestamp():
    raw = "00:01:22 Rahul: I will handle the authentication changes."
    segments = TranscriptParser.parse_text(raw)
    assert len(segments) == 1
    assert segments[0]["speaker_name"] == "Rahul"
    assert segments[0]["start_time"] == 82.0
    assert "authentication changes" in segments[0]["text"]

def test_parse_speaker_no_timestamp():
    raw = "Priya: We should test the payment flow before release."
    segments = TranscriptParser.parse_text(raw)
    assert len(segments) == 1
    assert segments[0]["speaker_name"] == "Priya"
    assert segments[0]["start_time"] is None

def test_unattributed_text_leaves_speaker_none():
    raw = "This is a general meeting note without an identified speaker label."
    segments = TranscriptParser.parse_text(raw)
    assert len(segments) == 1
    assert segments[0]["speaker_name"] is None
    assert segments[0]["text"] == raw

def test_parse_webvtt():
    raw = """WEBVTT

1
00:00:05.000 --> 00:00:10.000
<v Vikram>I will run the benchmark tests.
"""
    segments = TranscriptParser.parse_text(raw)
    assert len(segments) == 1
    assert segments[0]["speaker_name"] == "Vikram"
    assert segments[0]["start_time"] == 5.0
    assert segments[0]["end_time"] == 10.0
    assert "benchmark tests" in segments[0]["text"]

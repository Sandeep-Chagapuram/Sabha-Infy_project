import pytest
from app.ai.context_sieve import ContextSieve

def test_sieve_removes_exact_duplicates():
    segments = [
        {"id": "s1", "sequence_number": 0, "speaker_name": "Alice", "text": "We need to deploy by Friday.", "start_time": 0.0},
        {"id": "s2", "sequence_number": 1, "speaker_name": "Alice", "text": "We need to deploy by Friday.", "start_time": 2.0},  # Audio stutter duplicate
        {"id": "s3", "sequence_number": 2, "speaker_name": "Bob", "text": "I will prepare the Docker container.", "start_time": 4.0}
    ]
    packet = ContextSieve.process("test_meet", segments)
    assert packet.total_raw_segments == 3
    assert packet.excluded_segments_count >= 1
    # Check that duplicate was excluded
    included_texts = [s.text for s in packet.included_segments]
    assert len(included_texts) == 2

def test_sieve_preserves_negation_and_corrections():
    segments = [
        {"id": "s1", "sequence_number": 0, "speaker_name": "Priya", "text": "Can you ship the auth module tomorrow?"},
        {"id": "s2", "sequence_number": 1, "speaker_name": "Rahul", "text": "Actually no, I cannot do that because the token schema is not ready."},
        {"id": "s3", "sequence_number": 2, "speaker_name": "Priya", "text": "Understood, we won't ship it yet."}
    ]
    packet = ContextSieve.process("test_meet", segments)
    # Negation and correction segments must be included
    tags = [tag for s in packet.included_segments for tag in s.intent_tags]
    assert "negation_or_correction" in tags

def test_sieve_token_estimation_and_compression():
    long_text = "Hello team. Yeah. Okay. Sure. " * 10
    segments = [
        {"id": "s1", "sequence_number": 0, "speaker_name": "Host", "text": "We decided to increase the budget by $10,000."},
        {"id": "s2", "sequence_number": 1, "speaker_name": "Member", "text": "Yeah."},
        {"id": "s3", "sequence_number": 2, "speaker_name": "Member", "text": "Okay."},
        {"id": "s4", "sequence_number": 3, "speaker_name": "Member", "text": "Sure."},
        {"id": "s5", "sequence_number": 4, "speaker_name": "Host", "text": "Vikram will write the proposal before Monday."}
    ]
    packet = ContextSieve.process("test_meet", segments)
    assert packet.raw_token_count > 0
    assert packet.compressed_token_count > 0
    assert "<s1>" in packet.context_text
    assert "<s5>" in packet.context_text

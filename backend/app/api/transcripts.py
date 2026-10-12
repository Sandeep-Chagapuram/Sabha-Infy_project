from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user, get_current_workspace_member
from app.models.user import User, WorkspaceMember
from app.models.meeting import Meeting, TranscriptSegment, TranscriptCorrection, MeetingInputSource, MeetingStatus, SegmentStatus
from app.schemas.transcript import (
    TranscriptSegmentCreate,
    TranscriptSegmentResponse,
    TranscriptCorrectionCreate,
    TranscriptCorrectionResponse,
    PastedTranscriptRequest,
    TokenCountEstimate
)
from app.meetings.transcript_parser import TranscriptParser
from app.ai.context_sieve import ContextSieve
from app.websocket.manager import ws_manager

router = APIRouter()

@router.post("/workspaces/{workspace_id}/transcript-lab/estimate", response_model=TokenCountEstimate)
def estimate_transcript(content: str):
    words = content.split()
    word_count = len(words)
    char_count = len(content)
    tokens = ContextSieve.estimate_tokens(content)
    # Estimate routine Qualcomm Llama-3.1-8B cost ($0.05 / 1M)
    cost = round((tokens / 1_000_000.0) * 0.05, 6)
    parsed = TranscriptParser.parse_text(content)
    return TokenCountEstimate(
        word_count=word_count,
        char_count=char_count,
        estimated_tokens=tokens,
        estimated_cost_usd=cost,
        segment_count=len(parsed)
    )

@router.post("/workspaces/{workspace_id}/transcript-lab/paste")
def paste_transcript(
    workspace_id: str,
    req: PastedTranscriptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    if not req.content or not req.content.strip():
        raise HTTPException(status_code=400, detail="Transcript content cannot be empty.")

    # 1. Parse content
    parsed_segments = TranscriptParser.parse_text(req.content)
    if not parsed_segments:
        raise HTTPException(status_code=400, detail="Could not parse any transcript segments.")

    # 2. Create Meeting Record
    meeting_date = datetime.utcnow()
    if req.meeting_date:
        try:
            meeting_date = datetime.fromisoformat(req.meeting_date.replace('Z', '+00:00'))
        except Exception:
            pass

    meeting = Meeting(
        workspace_id=workspace_id,
        title=req.title or "Pasted Transcript Session",
        input_source=MeetingInputSource.PASTED_TRANSCRIPT,
        status=MeetingStatus.COMPLETED,
        meeting_date=meeting_date,
        timezone=req.timezone or "UTC",
        project_context=req.project_context
    )
    db.add(meeting)
    db.flush()

    # 3. Store Segments
    for seg in parsed_segments:
        ts = TranscriptSegment(
            meeting_id=meeting.id,
            sequence_number=seg["sequence_number"],
            speaker_name=seg["speaker_name"],
            text=seg["text"],
            start_time=seg["start_time"],
            end_time=seg["end_time"],
            status=SegmentStatus.FINAL
        )
        db.add(ts)

    db.commit()
    db.refresh(meeting)

    return {
        "meeting_id": meeting.id,
        "title": meeting.title,
        "segment_count": len(parsed_segments),
        "status": meeting.status.value,
        "message": "Transcript successfully loaded into Transcript Lab. Ready for analysis."
    }

@router.post("/workspaces/{workspace_id}/transcript-lab/upload")
async def upload_transcript(
    workspace_id: str,
    title: str = Form(...),
    file: UploadFile = File(...),
    timezone: Optional[str] = Form("UTC"),
    project_context: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    # Check extension
    filename = file.filename or "transcript.txt"
    if not (filename.endswith(".txt") or filename.endswith(".md") or filename.endswith(".vtt")):
        raise HTTPException(status_code=400, detail="Only .txt, .md, and .vtt transcript files are supported.")

    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = content_bytes.decode("latin-1")

    parsed_segments = TranscriptParser.parse_text(content)
    if not parsed_segments:
        raise HTTPException(status_code=400, detail="Uploaded file contained no valid transcript segments.")

    meeting = Meeting(
        workspace_id=workspace_id,
        title=title,
        input_source=MeetingInputSource.UPLOADED_TRANSCRIPT,
        status=MeetingStatus.COMPLETED,
        meeting_date=datetime.utcnow(),
        timezone=timezone or "UTC",
        project_context=project_context
    )
    db.add(meeting)
    db.flush()

    for seg in parsed_segments:
        ts = TranscriptSegment(
            meeting_id=meeting.id,
            sequence_number=seg["sequence_number"],
            speaker_name=seg["speaker_name"],
            text=seg["text"],
            start_time=seg["start_time"],
            end_time=seg["end_time"],
            status=SegmentStatus.FINAL
        )
        db.add(ts)

    db.commit()
    return {
        "meeting_id": meeting.id,
        "title": meeting.title,
        "filename": filename,
        "segment_count": len(parsed_segments),
        "message": "Transcript file imported successfully."
    }

@router.post("/workspaces/{workspace_id}/transcript-lab/upload-audio")
async def upload_audio(
    workspace_id: str,
    title: str = Form(...),
    file: UploadFile = File(...),
    timezone: Optional[str] = Form("UTC"),
    project_context: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    from app.meetings.audio_transcription import AudioTranscriptionService

    content_bytes = await file.read()
    res = await AudioTranscriptionService.transcribe_audio_file(
        file_bytes=content_bytes,
        filename=file.filename or "audio.mp3"
    )

    if not res.is_success:
        raise HTTPException(
            status_code=400,
            detail=res.message or "Audio transcription failed."
        )

    meeting = Meeting(
        workspace_id=workspace_id,
        title=title,
        input_source=MeetingInputSource.UPLOADED_AUDIO,
        status=MeetingStatus.COMPLETED,
        meeting_date=datetime.utcnow(),
        timezone=timezone or "UTC",
        project_context=project_context,
        duration_seconds=int(res.duration_seconds or 0)
    )
    db.add(meeting)
    db.flush()

    for seg in res.segments:
        ts = TranscriptSegment(
            meeting_id=meeting.id,
            sequence_number=seg["sequence_number"],
            speaker_name=seg.get("speaker_name"),
            text=seg["text"],
            start_time=seg.get("start_time"),
            end_time=seg.get("end_time"),
            status=SegmentStatus.FINAL
        )
        db.add(ts)

    db.commit()
    return {
        "meeting_id": meeting.id,
        "title": meeting.title,
        "filename": file.filename,
        "segment_count": len(res.segments),
        "duration_seconds": res.duration_seconds,
        "message": "Audio file transcribed and imported successfully."
    }

@router.get("/workspaces/{workspace_id}/meetings/{meeting_id}/segments", response_model=List[TranscriptSegmentResponse])
def get_segments(
    workspace_id: str,
    meeting_id: str,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    return (
        db.query(TranscriptSegment)
        .filter(TranscriptSegment.meeting_id == meeting_id, TranscriptSegment.is_deleted == False)
        .order_by(TranscriptSegment.sequence_number.asc())
        .all()
    )

@router.post("/workspaces/{workspace_id}/meetings/{meeting_id}/segments", response_model=TranscriptSegmentResponse)
async def add_segment(
    workspace_id: str,
    meeting_id: str,
    seg_in: TranscriptSegmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.workspace_id == workspace_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    seg = TranscriptSegment(
        meeting_id=meeting_id,
        sequence_number=seg_in.sequence_number,
        speaker_name=seg_in.speaker_name or current_user.full_name,
        speaker_user_id=current_user.id,
        text=seg_in.text,
        start_time=seg_in.start_time,
        end_time=seg_in.end_time,
        status=seg_in.status
    )
    db.add(seg)
    db.commit()
    db.refresh(seg)

    # Broadcast to room via WebSocket
    if meeting.livekit_room_name:
        await ws_manager.broadcast_to_room(
            meeting.livekit_room_name,
            {
                "event": "new_segment",
                "segment": TranscriptSegmentResponse.from_orm(seg).dict()
            }
        )

    return seg

@router.post("/workspaces/{workspace_id}/meetings/{meeting_id}/segments/{segment_id}/correct", response_model=TranscriptCorrectionResponse)
def correct_segment(
    workspace_id: str,
    meeting_id: str,
    segment_id: str,
    corr_in: TranscriptCorrectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    seg = db.query(TranscriptSegment).filter(TranscriptSegment.id == segment_id, TranscriptSegment.meeting_id == meeting_id).first()
    if not seg:
        raise HTTPException(status_code=404, detail="Segment not found.")

    corr = TranscriptCorrection(
        segment_id=seg.id,
        user_id=current_user.id,
        previous_text=seg.text,
        corrected_text=corr_in.corrected_text,
        reason=corr_in.reason
    )
    db.add(corr)
    seg.text = corr_in.corrected_text
    db.commit()
    db.refresh(corr)

    return corr

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
import io
import csv

from app.api.deps import get_db, get_current_workspace_member
from app.models.user import WorkspaceMember
from app.models.meeting import Meeting, TranscriptSegment
from app.models.task import Task
from app.models.intelligence import Decision, Risk

router = APIRouter()

@router.get("/workspaces/{workspace_id}/meetings/{meeting_id}/export")
def export_meeting(
    workspace_id: str,
    meeting_id: str,
    format: str = Query("markdown", regex="^(markdown|csv|json)$"),
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.workspace_id == workspace_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    segments = (
        db.query(TranscriptSegment)
        .filter(TranscriptSegment.meeting_id == meeting_id)
        .order_by(TranscriptSegment.sequence_number.asc())
        .all()
    )
    tasks = db.query(Task).filter(Task.meeting_id == meeting_id).all()
    decisions = db.query(Decision).filter(Decision.meeting_id == meeting_id).all()
    risks = db.query(Risk).filter(Risk.meeting_id == meeting_id).all()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Type", "Title / Content", "Speaker / Assignee", "Deadline / Status", "Evidence Quote"])

        for s in segments:
            writer.writerow(["Transcript Segment", s.text, s.speaker_name or "Unknown", "", ""])
        for t in tasks:
            writer.writerow(["Task", t.title, t.assignee_name or "Unassigned", f"{t.status.value} ({t.deadline_text or 'No deadline'})", t.source_evidence_quote])
        for d in decisions:
            writer.writerow(["Decision", d.title, "", d.status.value, d.source_evidence_quote])
        for r in risks:
            writer.writerow(["Risk", r.title, "", r.severity.value, r.source_evidence_quote])

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sabha_meeting_{meeting_id[:8]}.csv"}
        )

    elif format == "json":
        data = {
            "meeting_id": meeting.id,
            "title": meeting.title,
            "meeting_date": meeting.meeting_date.isoformat(),
            "timezone": meeting.timezone,
            "project_context": meeting.project_context,
            "transcript_segments": [
                {"seq": s.sequence_number, "speaker": s.speaker_name, "text": s.text, "start_time": s.start_time}
                for s in segments
            ],
            "tasks": [
                {"title": t.title, "assignee": t.assignee_name, "status": t.status.value, "evidence": t.source_evidence_quote}
                for t in tasks
            ],
            "decisions": [
                {"title": d.title, "status": d.status.value, "evidence": d.source_evidence_quote}
                for d in decisions
            ],
            "risks": [
                {"title": r.title, "severity": r.severity.value, "evidence": r.source_evidence_quote}
                for r in risks
            ]
        }
        return data

    else:  # Markdown
        md = []
        md.append(f"# Sabha AI Meeting Intelligence Report: {meeting.title}\n")
        md.append(f"**Date:** {meeting.meeting_date.strftime('%Y-%m-%d %H:%M UTC')} | **Timezone:** {meeting.timezone}\n")
        md.append(f"**Input Source:** {meeting.input_source.value} | **Tokens:** {meeting.compressed_token_count} (Raw: {meeting.raw_token_count})\n")
        md.append("\n---\n")

        md.append("## Confirmed Decisions\n")
        if decisions:
            for d in decisions:
                md.append(f"- **{d.title}** ({d.status.value})")
                md.append(f"  > *Evidence:* \"{d.source_evidence_quote}\"\n")
        else:
            md.append("*No decisions recorded.*\n")

        md.append("\n## Action Items & Tasks\n")
        if tasks:
            for t in tasks:
                owner = t.assignee_name or "Unassigned (Pending Confirmation)"
                deadline = t.deadline_text or "Unspecified"
                md.append(f"- [ ] **{t.title}**")
                md.append(f"  - **Owner:** {owner} | **Deadline:** {deadline} | **Status:** {t.status.value} | **Priority:** {t.priority.value}")
                md.append(f"  > *Evidence:* \"{t.source_evidence_quote}\"\n")
        else:
            md.append("*No action items recorded.*\n")

        md.append("\n## Risks & Blind Spots\n")
        if risks:
            for r in risks:
                md.append(f"- **[{r.severity.value.upper()}] {r.title}**")
                md.append(f"  - *Impact:* {r.potential_impact or 'N/A'}")
                md.append(f"  - *Mitigation:* {r.suggested_mitigation or 'N/A'}")
                md.append(f"  > *Evidence:* \"{r.source_evidence_quote}\"\n")
        else:
            md.append("*No critical risks flagged.*\n")

        md.append("\n---\n*Report generated by Sabha AI: Every conversation. A smarter decision.*")

        return Response(
            content="\n".join(md),
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=sabha_report_{meeting_id[:8]}.md"}
        )

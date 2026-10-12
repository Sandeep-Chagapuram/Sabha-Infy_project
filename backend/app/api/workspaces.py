from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.api.deps import get_db, get_current_user, get_current_workspace_member, require_workspace_role
from app.models.user import User, Workspace, WorkspaceMember, UserRole
from app.schemas.auth import WorkspaceCreate, WorkspaceResponse, MemberInvite, WorkspaceMemberResponse

router = APIRouter()

@router.post("/workspaces", response_model=WorkspaceResponse)
def create_workspace(
    ws_in: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    slug = f"{ws_in.name.lower().replace(' ', '-')}-{str(uuid.uuid4())[:8]}"
    ws = Workspace(name=ws_in.name, slug=slug)
    db.add(ws)
    db.flush()

    member = WorkspaceMember(
        workspace_id=ws.id,
        user_id=current_user.id,
        role=UserRole.ADMIN
    )
    db.add(member)
    db.commit()
    db.refresh(ws)

    return WorkspaceResponse(
        id=ws.id,
        name=ws.name,
        slug=ws.slug,
        created_at=ws.created_at,
        role=UserRole.ADMIN
    )

@router.get("/workspaces/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
def list_workspace_members(
    workspace_id: str,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    members = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
    results = []
    for m in members:
        u = m.user
        results.append(
            WorkspaceMemberResponse(
                id=m.id,
                user_id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=m.role,
                created_at=m.created_at
            )
        )
    return results

@router.post("/workspaces/{workspace_id}/invite")
def invite_member(
    workspace_id: str,
    invite: MemberInvite,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_workspace_role(UserRole.ADMIN))
):
    target_user = db.query(User).filter(User.email == invite.email).first()
    if not target_user:
        raise HTTPException(
            status_code=404,
            detail=f"User with email '{invite.email}' not found. Please ask them to register first."
        )

    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == target_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this workspace.")

    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=target_user.id,
        role=invite.role
    )
    db.add(new_member)
    db.commit()

    return {"message": f"User {invite.email} invited with role {invite.role.value}"}

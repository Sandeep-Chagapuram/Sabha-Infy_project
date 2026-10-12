from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, Workspace, WorkspaceMember, UserRole
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse, WorkspaceResponse
import uuid

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    # Create user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(user)
    db.flush()

    # Create default workspace
    ws_name = user_in.workspace_name or f"{user_in.full_name}'s Workspace"
    slug = f"{ws_name.lower().replace(' ', '-')}-{str(uuid.uuid4())[:8]}"
    workspace = Workspace(name=ws_name, slug=slug)
    db.add(workspace)
    db.flush()

    # Add user as workspace ADMIN
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role=UserRole.ADMIN
    )
    db.add(member)
    db.commit()

    token = create_access_token(subject=user.id)
    return Token(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        default_workspace_id=workspace.id
    )

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    # Find default workspace
    membership = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == user.id).first()
    ws_id = membership.workspace_id if membership else None

    token = create_access_token(subject=user.id)
    return Token(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        default_workspace_id=ws_id
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me/workspaces", response_model=list[WorkspaceResponse])
def get_my_workspaces(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).all()
    results = []
    for m in memberships:
        ws = m.workspace
        results.append(
            WorkspaceResponse(
                id=ws.id,
                name=ws.name,
                slug=ws.slug,
                created_at=ws.created_at,
                role=m.role
            )
        )
    return results

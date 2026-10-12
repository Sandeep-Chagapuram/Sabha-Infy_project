from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    default_workspace_id: Optional[str] = None

class TokenData(BaseModel):
    user_id: Optional[str] = None

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    workspace_name: Optional[str] = "Default Workspace"

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class WorkspaceMemberResponse(BaseModel):
    id: str
    user_id: str
    email: str
    full_name: str
    role: UserRole
    created_at: datetime

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    role: Optional[UserRole] = None

    class Config:
        from_attributes = True

class WorkspaceCreate(BaseModel):
    name: str

class MemberInvite(BaseModel):
    email: str
    role: UserRole = UserRole.PARTICIPANT

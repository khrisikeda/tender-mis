import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from app.core.enums import RoleName


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: RoleName
    department: Optional[str] = None
    phone: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: EmailStr
    department: Optional[str]
    is_active: bool
    created_at: datetime
    role: str  # flattened from the Role relationship in the router

    @classmethod
    def from_orm_user(cls, user):
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            department=user.department,
            is_active=user.is_active,
            created_at=user.created_at,
            role=user.role.name,
        )


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

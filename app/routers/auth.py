from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.deps import get_current_user, require_roles
from app.core.audit import write_audit_log
from app.core.enums import AuditAction, RoleName
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserOut, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed attempts too -- useful for detecting credential stuffing.
        write_audit_log(
            db,
            user_id=user.id if user else None,
            action=AuditAction.LOGIN_FAILED,
            entity_type="user",
            entity_id=user.id if user else None,
            ip_address=request.client.host if request.client else None,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    user.last_login_at = datetime.utcnow()
    write_audit_log(
        db,
        user_id=user.id,
        action=AuditAction.LOGIN,
        entity_type="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    db.commit()

    access_token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.name})
    refresh_token = create_refresh_token(subject=str(user.id))

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access_token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.name})
    new_refresh_token = create_refresh_token(subject=str(user.id))
    return Token(access_token=new_access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return UserOut.from_orm_user(current_user)


@router.post(
    "/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([RoleName.ADMIN]))],
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin-only: create a new user account with an assigned role."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    role = db.query(Role).filter(Role.name == payload.role.value).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role '{payload.role}' not found -- run the seed script")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        department=payload.department,
        phone=payload.phone,
        role_id=role.id,
    )
    db.add(user)
    db.flush()  # get user.id before commit

    write_audit_log(
        db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="user",
        entity_id=user.id,
        new_value={"email": user.email, "role": role.name},
    )
    db.commit()
    db.refresh(user)

    return UserOut.from_orm_user(user)

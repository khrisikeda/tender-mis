from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import decode_token
from app.core.enums import RoleName
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_roles(allowed_roles: Iterable[RoleName]):
    """
    Dependency factory for endpoint-level RBAC, e.g.:

        @router.post("/sources", dependencies=[Depends(require_roles([RoleName.ADMIN]))])

    Enforced server-side -- this is the actual permission boundary, not the UI.
    """
    allowed_names = {r.value for r in allowed_roles}

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in allowed_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.name}' is not permitted to perform this action.",
            )
        return current_user

    return checker

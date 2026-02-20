from typing import TypedDict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.db import get_db, set_org_context
from core.security import TokenError, decode_access_token

bearer_scheme = HTTPBearer(auto_error=True)


class CurrentUser(TypedDict):
    email: str
    org_id: int
    role: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    org_id = int(payload["org_id"])
    set_org_context(db, org_id)
    return {
        "email": str(payload["sub"]),
        "org_id": org_id,
        "role": str(payload.get("role", "manager")),
    }


def require_owner(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user["role"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner access required")
    return user

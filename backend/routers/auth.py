from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from core.config import settings
from core.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

_USERS = {
    settings.owner_email: {
        "password_hash": hash_password(settings.owner_password),
        "org_id": settings.owner_org_id,
        "role": "owner",
    }
}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login(payload: LoginRequest):
    user = _USERS.get(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        subject=payload.email,
        org_id=int(user["org_id"]),
        role=str(user["role"]),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "org_id": user["org_id"],
        "role": user["role"],
    }

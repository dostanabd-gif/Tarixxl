from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.orm import Session

from core.db import get_db
from core.security import create_access_token, verify_password
from services.user_service import get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, str(payload.email))
    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, str(user["password_hash"])):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        subject=str(user["email"]),
        org_id=int(user["org_id"]),
        role=str(user["role"]),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "org_id": int(user["org_id"]),
        "role": str(user["role"]),
    }

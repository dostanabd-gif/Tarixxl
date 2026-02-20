from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.orm import Session

from core.db import get_db
from core.deps import CurrentUser, get_current_user
from core.security import create_access_token, verify_password
from services.user_service import get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    org_id: int
    role: str


@router.post("/login", response_model=LoginResponse, summary="Вход пользователя")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, str(payload.email))
    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    if not verify_password(payload.password, str(user["password_hash"])):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

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


@router.get("/me", summary="Текущий пользователь")
def me(user: CurrentUser = Depends(get_current_user)):
    return user

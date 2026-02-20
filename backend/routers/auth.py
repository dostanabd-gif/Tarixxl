from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy.orm import Session

from core.config import settings
from core.db import get_db
from core.deps import CurrentUser, get_current_user
from core.security import create_access_token, verify_password
from services.user_service import get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    login: str | None = None
    email: str | None = None
    password: str

    @model_validator(mode="after")
    def validate_login_source(self):
        if not self.login and not self.email:
            raise ValueError("login or email is required")
        return self


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    org_id: int
    role: str


def resolve_login_to_email(login: str) -> str:
    normalized = login.strip().lower()
    if "@" in normalized:
        return normalized
    if normalized in {"admin", "owner"}:
        return settings.owner_email
    return normalized


@router.post("/login", response_model=LoginResponse, summary="Вход пользователя")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    source = payload.login or payload.email or ""
    email = resolve_login_to_email(source)
    user = get_user_by_email(db, email)
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

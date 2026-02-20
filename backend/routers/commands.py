from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import pyotp

from ai_engine.economy_engine import WhatIfInput, evaluate_command
from core.config import settings
from core.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/commands", tags=["commands"])


class WhatIfRequest(BaseModel):
    energy_kwh_delta: float
    feed_kg_delta: float
    mortality_delta_birds: int
    revenue_delta: float


class SetPointRequest(BaseModel):
    command: str
    value: float
    otp_code: str


@router.post("/what-if")
def what_if(payload: WhatIfRequest, _: CurrentUser = Depends(get_current_user)):
    result = evaluate_command(WhatIfInput(**payload.model_dump()))
    return result.__dict__


@router.post("/setpoint")
def setpoint(payload: SetPointRequest, _: CurrentUser = Depends(get_current_user)):
    totp = pyotp.TOTP(settings.command_2fa_secret)
    if not totp.verify(payload.otp_code, valid_window=1):
        raise HTTPException(status_code=403, detail="2FA code invalid")
    return {"status": "queued", "command": payload.command, "value": payload.value}

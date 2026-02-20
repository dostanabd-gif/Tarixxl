import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import pyotp
from sqlalchemy import text
from sqlalchemy.orm import Session

from ai_engine.economy_engine import WhatIfInput, evaluate_command
from core.config import settings
from core.db import get_db
from core.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/commands", tags=["commands"])


class WhatIfRequest(BaseModel):
    energy_kwh_delta: float
    feed_kg_delta: float
    mortality_delta_birds: int
    revenue_delta: float


class SetPointRequest(BaseModel):
    node_id: str
    command: str
    value: float
    otp_code: str


@router.post("/what-if")
def what_if(payload: WhatIfRequest, _: CurrentUser = Depends(get_current_user)):
    result = evaluate_command(WhatIfInput(**payload.model_dump()))
    return result.__dict__


@router.post("/setpoint")
def setpoint(
    payload: SetPointRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    totp = pyotp.TOTP(settings.command_2fa_secret)
    if not totp.verify(payload.otp_code, valid_window=1):
        raise HTTPException(status_code=403, detail="2FA code invalid")

    row = db.execute(
        text(
            """
            INSERT INTO edge_command_queue (org_id, node_id, command, payload, status)
            VALUES (:org_id, :node_id, :command, CAST(:payload AS jsonb), 'queued')
            RETURNING id
            """
        ),
        {
            "org_id": user["org_id"],
            "node_id": payload.node_id,
            "command": payload.command,
            "payload": json.dumps({"value": payload.value}),
        },
    ).mappings().first()
    db.commit()
    return {
        "status": "queued",
        "queue_id": row["id"] if row else None,
        "command": payload.command,
        "value": payload.value,
    }

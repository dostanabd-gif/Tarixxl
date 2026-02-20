from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.config import settings
from core.db import get_db
from core.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/billing", tags=["billing"])


class SavingsRecord(BaseModel):
    period: str
    documented_savings: float


@router.post("/savings-log")
def savings_log(
    payload: SavingsRecord,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    success_fee = round(payload.documented_savings * 0.12, 2)
    row = db.execute(
        text(
            """
            INSERT INTO savings_log (org_id, period, documented_savings, success_fee)
            VALUES (:org_id, :period, :documented_savings, :success_fee)
            RETURNING id, org_id, period, documented_savings, success_fee, created_at
            """
        ),
        {
            "org_id": user["org_id"],
            "period": payload.period,
            "documented_savings": payload.documented_savings,
            "success_fee": success_fee,
        },
    ).mappings().first()
    db.commit()
    return dict(row) if row else {}


@router.get("/invoice")
def invoice(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    rows = db.execute(
        text(
            """
            SELECT period, documented_savings, success_fee, created_at
            FROM savings_log
            WHERE org_id = :org_id
            ORDER BY created_at DESC
            """
        ),
        {"org_id": user["org_id"]},
    ).mappings().all()
    total_fee = round(sum(float(item["success_fee"]) for item in rows), 2)
    return {
        "org_id": user["org_id"],
        "currency": settings.currency,
        "items": [dict(item) for item in rows],
        "total_success_fee": total_fee,
    }

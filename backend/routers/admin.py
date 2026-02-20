from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.db import get_db
from core.deps import CurrentUser, require_owner

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/metrics")
def platform_metrics(
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_owner),
):
    row = db.execute(
        text(
            """
            SELECT COUNT(DISTINCT org_id) AS active_customers,
                   COALESCE(SUM(success_fee), 0) AS mrr
            FROM savings_log
            WHERE created_at >= date_trunc('month', NOW())
            """
        )
    ).mappings().first()

    active_customers = int(row["active_customers"] if row else 0)
    mrr = round(float(row["mrr"] if row else 0), 2)
    return {"active_customers": active_customers, "mrr": mrr, "arr": round(mrr * 12, 2)}

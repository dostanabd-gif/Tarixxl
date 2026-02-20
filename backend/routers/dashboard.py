from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.db import get_db
from core.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    row = db.execute(
        text(
            """
            SELECT
                AVG(temp_c) AS temperature,
                AVG(humidity_pct) AS humidity,
                AVG(co2_ppm) AS co2,
                AVG(nh3_ppm) AS nh3,
                SUM(feed_kg) AS feed,
                SUM(water_l) AS water,
                SUM(energy_kwh) AS energy
            FROM telemetry
            WHERE org_id = :org_id
              AND ts >= NOW() - INTERVAL '24 hours'
            """
        ),
        {"org_id": user["org_id"]},
    ).mappings().first()

    result = dict(row) if row else {}
    return {
        "temperature": round(float(result.get("temperature") or 0), 2),
        "humidity": round(float(result.get("humidity") or 0), 2),
        "co2": round(float(result.get("co2") or 0), 2),
        "nh3": round(float(result.get("nh3") or 0), 2),
        "feed": round(float(result.get("feed") or 0), 2),
        "water": round(float(result.get("water") or 0), 2),
        "energy": round(float(result.get("energy") or 0), 2),
    }

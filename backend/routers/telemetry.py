from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.db import get_db
from core.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class TelemetryIn(BaseModel):
    farm_id: int
    temp_c: float
    humidity_pct: float
    co2_ppm: float
    nh3_ppm: float
    feed_kg: float
    water_l: float
    energy_kwh: float


@router.post("")
def ingest(
    payload: TelemetryIn,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    values = payload.model_dump()
    db.execute(
        text(
            """
            INSERT INTO telemetry (
                ts, org_id, farm_id, temp_c, humidity_pct, co2_ppm, nh3_ppm, feed_kg, water_l, energy_kwh
            ) VALUES (
                NOW(), :org_id, :farm_id, :temp_c, :humidity_pct, :co2_ppm, :nh3_ppm, :feed_kg, :water_l, :energy_kwh
            )
            """
        ),
        {"org_id": user["org_id"], **values},
    )
    db.commit()
    return {"status": "accepted"}


@router.get("/latest")
def latest(
    limit: int = 20,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    rows = db.execute(
        text(
            """
            SELECT ts, farm_id, temp_c, humidity_pct, co2_ppm, nh3_ppm, feed_kg, water_l, energy_kwh
            FROM telemetry
            WHERE org_id = :org_id
            ORDER BY ts DESC
            LIMIT :limit
            """
        ),
        {"org_id": user["org_id"], "limit": limit},
    ).mappings()
    return {"items": [dict(row) for row in rows]}

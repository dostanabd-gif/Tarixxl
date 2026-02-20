from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.db import get_db
from core.deps import CurrentUser, get_current_user
from services.sync_service import TelemetryEvent, insert_telemetry_batch

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class TelemetryIn(BaseModel):
    event_id: str | None = None
    ts: str | None = None
    farm_id: int
    temp_c: float
    humidity_pct: float
    co2_ppm: float
    nh3_ppm: float
    feed_kg: float
    water_l: float
    energy_kwh: float


class TelemetryBatchIn(BaseModel):
    events: list[TelemetryIn]


@router.post("")
def ingest(
    payload: TelemetryIn,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    event = TelemetryEvent(
        event_id=payload.event_id or str(uuid4()),
        ts=payload.ts,
        farm_id=payload.farm_id,
        temp_c=payload.temp_c,
        humidity_pct=payload.humidity_pct,
        co2_ppm=payload.co2_ppm,
        nh3_ppm=payload.nh3_ppm,
        feed_kg=payload.feed_kg,
        water_l=payload.water_l,
        energy_kwh=payload.energy_kwh,
    )
    inserted = insert_telemetry_batch(db, user["org_id"], [event])
    db.commit()
    return {"status": "accepted", "inserted": inserted, "event_id": event.event_id}


@router.post("/batch")
def ingest_batch(
    payload: TelemetryBatchIn,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    events = [
        TelemetryEvent(
            event_id=item.event_id or str(uuid4()),
            ts=item.ts,
            farm_id=item.farm_id,
            temp_c=item.temp_c,
            humidity_pct=item.humidity_pct,
            co2_ppm=item.co2_ppm,
            nh3_ppm=item.nh3_ppm,
            feed_kg=item.feed_kg,
            water_l=item.water_l,
            energy_kwh=item.energy_kwh,
        )
        for item in payload.events
    ]
    inserted = insert_telemetry_batch(db, user["org_id"], events)
    db.commit()
    return {"status": "accepted", "received": len(events), "inserted": inserted}


@router.get("/latest")
def latest(
    limit: int = 20,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    rows = db.execute(
        text(
            """
            SELECT event_id, ts, farm_id, temp_c, humidity_pct, co2_ppm, nh3_ppm, feed_kg, water_l, energy_kwh
            FROM telemetry
            WHERE org_id = :org_id
            ORDER BY ts DESC
            LIMIT :limit
            """
        ),
        {"org_id": user["org_id"], "limit": limit},
    ).mappings()
    return {"items": [dict(row) for row in rows]}

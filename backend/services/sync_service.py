from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(slots=True)
class TelemetryEvent:
    event_id: str
    farm_id: int
    temp_c: float
    humidity_pct: float
    co2_ppm: float
    nh3_ppm: float
    feed_kg: float
    water_l: float
    energy_kwh: float
    ts: str | None = None


def insert_telemetry_batch(db: Session, org_id: int, events: Sequence[TelemetryEvent]) -> int:
    inserted = 0
    for event in events:
        row = db.execute(
            text(
                """
                INSERT INTO telemetry (
                    event_id, ts, org_id, farm_id, temp_c, humidity_pct, co2_ppm, nh3_ppm, feed_kg, water_l, energy_kwh
                ) VALUES (
                    :event_id,
                    COALESCE(:ts::timestamptz, NOW()),
                    :org_id, :farm_id, :temp_c, :humidity_pct, :co2_ppm, :nh3_ppm, :feed_kg, :water_l, :energy_kwh
                )
                ON CONFLICT (event_id) DO NOTHING
                RETURNING event_id
                """
            ),
            {
                "event_id": event.event_id,
                "ts": event.ts,
                "org_id": org_id,
                "farm_id": event.farm_id,
                "temp_c": event.temp_c,
                "humidity_pct": event.humidity_pct,
                "co2_ppm": event.co2_ppm,
                "nh3_ppm": event.nh3_ppm,
                "feed_kg": event.feed_kg,
                "water_l": event.water_l,
                "energy_kwh": event.energy_kwh,
            },
        ).first()
        if row:
            inserted += 1
    return inserted

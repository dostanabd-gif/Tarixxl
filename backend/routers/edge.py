import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.db import get_db
from core.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/edge", tags=["edge"])


class HeartbeatIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str = Field(min_length=2, max_length=128)
    online: bool = True


class QueueCommandIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str = Field(min_length=2, max_length=128)
    command: str = Field(min_length=2, max_length=128)
    payload: dict


@router.post("/heartbeat")
def heartbeat(
    payload: HeartbeatIn,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    db.execute(
        text(
            """
            INSERT INTO edge_nodes (org_id, node_id, is_online, last_seen_at)
            VALUES (:org_id, :node_id, :is_online, NOW())
            ON CONFLICT (org_id, node_id)
            DO UPDATE SET is_online = EXCLUDED.is_online, last_seen_at = NOW()
            """
        ),
        {"org_id": user["org_id"], "node_id": payload.node_id, "is_online": payload.online},
    )
    db.commit()
    return {"status": "ok"}


@router.post("/commands")
def queue_command(
    payload: QueueCommandIn,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
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
            "payload": json.dumps(payload.payload),
        },
    ).mappings().first()
    db.commit()
    return {"status": "queued", "id": row["id"] if row else None}


@router.get("/commands/pending")
def get_pending_commands(
    node_id: str,
    limit: int = Query(default=20, ge=1, le=500),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    rows = db.execute(
        text(
            """
            SELECT id, command, payload, created_at
            FROM edge_command_queue
            WHERE org_id = :org_id AND node_id = :node_id AND status = 'queued'
            ORDER BY created_at ASC
            LIMIT :limit
            """
        ),
        {"org_id": user["org_id"], "node_id": node_id, "limit": limit},
    ).mappings().all()
    return {"items": [dict(r) for r in rows]}


@router.post("/commands/{command_id}/ack")
def ack_command(
    command_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    result = db.execute(
        text(
            """
            UPDATE edge_command_queue
            SET status = 'applied', applied_at = NOW()
            WHERE id = :id AND org_id = :org_id
            """
        ),
        {"id": command_id, "org_id": user["org_id"]},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Command not found")
    db.commit()
    return {"status": "applied", "id": command_id}

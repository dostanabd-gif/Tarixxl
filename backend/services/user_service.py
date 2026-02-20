from sqlalchemy import text
from sqlalchemy.orm import Session

from core.config import settings
from core.security import hash_password


def get_user_by_email(db: Session, email: str):
    return db.execute(
        text(
            """
            SELECT id, org_id, email, password_hash, role, is_active
            FROM users
            WHERE email = :email
            """
        ),
        {"email": email},
    ).mappings().first()


def ensure_bootstrap_owner(db: Session) -> None:
    org = db.execute(
        text(
            """
            INSERT INTO organizations (name)
            VALUES ('Default organization')
            ON CONFLICT DO NOTHING
            RETURNING id
            """
        )
    ).mappings().first()

    org_id = settings.owner_org_id
    if org:
        org_id = int(org["id"])

    exists = db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": settings.owner_email},
    ).first()
    if exists:
        return

    db.execute(
        text(
            """
            INSERT INTO users (org_id, email, password_hash, role, is_active)
            VALUES (:org_id, :email, :password_hash, 'owner', true)
            """
        ),
        {
            "org_id": org_id,
            "email": settings.owner_email,
            "password_hash": hash_password(settings.owner_password),
        },
    )

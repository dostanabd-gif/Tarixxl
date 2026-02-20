from fastapi import FastAPI

from core.config import settings
from core.db import SessionLocal
from routers import admin, auth, billing, commands, dashboard, edge, telemetry
from services.user_service import ensure_bootstrap_owner

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def bootstrap_owner() -> None:
    db = SessionLocal()
    try:
        ensure_bootstrap_owner(db)
        db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"service": settings.app_name, "environment": settings.environment}


@app.get("/health")
def health():
    return {"status": "ok", "message": "FarmIoT API работает!"}


app.include_router(auth.router)
app.include_router(telemetry.router)
app.include_router(commands.router)
app.include_router(dashboard.router)
app.include_router(billing.router)
app.include_router(admin.router)
app.include_router(edge.router)

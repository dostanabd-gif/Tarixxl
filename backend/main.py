from fastapi import FastAPI

from core.config import settings
from core.db import SessionLocal
from routers import admin, ai_assistant, auth, billing, commands, dashboard, edge, telemetry
from services.user_service import ensure_bootstrap_owner

app = FastAPI(
    title="FarmIoT Platform API",
    description=(
        "Серьезный API-контур для SaaS управления птицефабрикой: "
        "аутентификация, телеметрия, команды, биллинг и edge-online/offline синхронизация."
    ),
    version="1.0.0",
    contact={"name": "FarmIoT Support", "email": "support@farmiot.local"},
)


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
    return {
        "service": "FarmIoT Platform API",
        "environment": settings.environment,
        "status": "operational",
        "modules": [
            "auth",
            "telemetry",
            "commands",
            "dashboard",
            "billing",
            "admin",
            "edge",
            "ai",
        ],
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "FarmIoT Platform API",
        "message": "Сервис работает стабильно",
    }


app.include_router(auth.router)
app.include_router(telemetry.router)
app.include_router(commands.router)
app.include_router(dashboard.router)
app.include_router(billing.router)
app.include_router(admin.router)
app.include_router(edge.router)
app.include_router(ai_assistant.router)

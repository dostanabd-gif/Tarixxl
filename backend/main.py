from fastapi import FastAPI

from core.config import settings
from routers import admin, auth, billing, commands, dashboard, telemetry

app = FastAPI(title=settings.app_name)


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

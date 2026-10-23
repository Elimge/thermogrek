from fastapi import APIRouter
from app.api.v1.endpoints import health, assets, telemetry, alarms, metrics

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(assets.router)
api_router.include_router(telemetry.router)
api_router.include_router(alarms.router)
api_router.include_router(metrics.router)

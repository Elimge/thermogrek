from typing import List
from fastapi import APIRouter, Depends
from psycopg import AsyncConnection
from app.db.session import get_db_connection
from app.db.repositories.telemetry_repo import TelemetryRepository
from app.schemas.responses import TimeSeriesPoint

router = APIRouter()

@router.get("/assets/{asset_id}/history", response_model=List[TimeSeriesPoint], tags=["Telemetry"])
async def get_historical_trend(
    asset_id: str, limit: int = 100, conn: AsyncConnection = Depends(get_db_connection)
):
    """Returns chronologically ordered time-series points for historical trend charting."""
    repo = TelemetryRepository(conn)
    return await repo.get_historical_telemetry(asset_id, min(limit, 500))

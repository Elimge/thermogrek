from typing import List
from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from app.db.session import get_db_connection
from app.db.repositories.asset_repo import AssetRepository
from app.db.repositories.telemetry_repo import TelemetryRepository
from app.schemas.responses import AssetSummary, LatestAssetReading

router = APIRouter()

@router.get("/assets", response_model=List[AssetSummary], tags=["Assets"])
async def list_assets(conn: AsyncConnection = Depends(get_db_connection)):
    """Returns list of active assets and their high-level health status."""
    repo = AssetRepository(conn)
    return await repo.get_all_active()

@router.get("/assets/{asset_id}", response_model=AssetSummary, tags=["Assets"])
async def get_asset_detail(asset_id: str, conn: AsyncConnection = Depends(get_db_connection)):
    """Returns asset metadata and specifications."""
    repo = AssetRepository(conn)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return asset

@router.get("/assets/{asset_id}/latest", response_model=LatestAssetReading, tags=["Assets"])
async def get_latest_reading(asset_id: str, conn: AsyncConnection = Depends(get_db_connection)):
    """Returns the most recent raw sensor readings and calculated thermodynamic KPIs."""
    repo = TelemetryRepository(conn)
    latest = await repo.get_latest_reading_and_kpis(asset_id)
    if not latest:
        raise HTTPException(status_code=404, detail=f"No telemetry readings found for {asset_id}")
    return latest

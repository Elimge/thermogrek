from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class AssetSummary(BaseModel):
    id: str
    plant_id: str
    name: str
    asset_type: str
    health_status: str
    is_active: bool
    created_at: datetime

class LatestAssetReading(BaseModel):
    asset_id: str
    timestamp: datetime
    metrics: Dict[str, Any]
    kpis: Dict[str, Any]
    health_status: str

class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    metrics: Dict[str, Any]

class AlarmItem(BaseModel):
    id: str
    triggered_at: datetime
    cleared_at: Optional[datetime] = None
    asset_id: str
    severity: str
    alarm_code: str
    message: str
    trigger_context: Dict[str, Any]
    acknowledged: bool

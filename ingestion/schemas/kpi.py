from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ThermodynamicKPIPayload(BaseModel):
    asset_id: str
    timestamp: datetime
    delta_t_c: Optional[float] = None
    delta_p_bar: Optional[float] = None
    heat_duty_kw: Optional[float] = None
    approach_temp_c: Optional[float] = None
    effectiveness_pct: Optional[float] = None
    health_index_pct: float = Field(..., ge=0.0, le=100.0)
    health_status: str  # NORMAL, WARNING, CRITICAL
    alarm_triggered: Optional[dict] = None

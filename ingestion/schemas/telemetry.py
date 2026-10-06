from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class HeatExchangerMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")

    t_hot_in_c: float = Field(..., ge=-20.0, le=250.0, description="Process oil inlet temp")
    t_hot_out_c: float = Field(..., ge=-20.0, le=250.0, description="Process oil outlet temp")
    t_cold_in_c: float = Field(..., ge=0.0, le=100.0, description="Cooling water inlet temp")
    t_cold_out_c: float = Field(..., ge=0.0, le=100.0, description="Cooling water outlet temp")
    p_in_bar: float = Field(..., ge=0.0, le=30.0, description="Inlet pressure")
    p_out_bar: float = Field(..., ge=0.0, le=30.0, description="Outlet pressure")
    flow_rate_m3h: float = Field(..., gt=0.0, le=200.0, description="Volumetric flow rate")


class CoolingTowerMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")

    t_water_in_c: float = Field(..., ge=0.0, le=100.0, description="Warm water inlet temp")
    t_water_out_c: float = Field(..., ge=0.0, le=100.0, description="Cold water basin temp")
    t_ambient_db_c: float = Field(..., ge=-30.0, le=60.0, description="Ambient dry bulb temp")
    relative_humidity_pct: float = Field(..., ge=1.0, le=100.0, description="Ambient relative humidity")
    fan_speed_rpm: float = Field(..., ge=0.0, le=3000.0, description="Fan rotational speed")
    water_flow_m3h: float = Field(..., gt=0.0, le=200.0, description="Circulating water flow")


class TelemetryEnvelope(BaseModel):
    asset_id: str = Field(..., min_length=2, max_length=50)
    timestamp: datetime
    metrics: dict
    operational_mode: Optional[str] = "NORMAL"

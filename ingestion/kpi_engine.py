import math
from typing import Tuple, Optional, Dict, Any
from schemas.telemetry import HeatExchangerMetrics, CoolingTowerMetrics
from schemas.kpi import ThermodynamicKPIPayload


def calculate_stull_wet_bulb(t_db: float, rh: float) -> float:
    """Calculates Wet-Bulb Temperature (Twb) using Stull's empirical psychrometric formula."""
    return (
        t_db * math.atan(0.151977 * math.sqrt(rh + 8.313659))
        + math.atan(t_db + rh)
        - math.atan(rh - 1.676331)
        + 0.00391838 * (rh ** 1.5) * math.atan(0.023101 * rh)
        - 4.686035
    )


class KPIEngine:
    # Heat Exchanger Baseline Constants
    HE_NOMINAL_DELTA_P_BAR = 0.70
    HE_CRITICAL_DELTA_P_BAR = 1.40
    CP_OIL = 2.0    # kJ/kg*K
    RHO_OIL = 880.0 # kg/m3

    # Cooling Tower Baseline Constants
    CT_DESIGN_APPROACH_C = 4.5
    CT_CRITICAL_APPROACH_C = 8.5

    @classmethod
    def evaluate_heat_exchanger(
        cls, asset_id: str, timestamp, metrics: HeatExchangerMetrics
    ) -> ThermodynamicKPIPayload:
        delta_t_hot = metrics.t_hot_in_c - metrics.t_hot_out_c
        delta_p = max(0.0, metrics.p_in_bar - metrics.p_out_bar)

        # Heat Duty: m_dot * Cp * delta_T (kW)
        mass_flow_kgs = (metrics.flow_rate_m3h * cls.RHO_OIL) / 3600.0
        heat_duty_kw = mass_flow_kgs * cls.CP_OIL * delta_t_hot

        # Health Index calculation based on hydraulic pressure drop degradation:
        # 100% when Delta P <= 0.70 bar; decays towards 0% as Delta P approaches 1.80 bar
        delta_p_excess = max(0.0, delta_p - cls.HE_NOMINAL_DELTA_P_BAR)
        health_index = max(0.0, 100.0 - (delta_p_excess / (cls.HE_CRITICAL_DELTA_P_BAR - cls.HE_NOMINAL_DELTA_P_BAR) * 50.0))
        health_index = round(min(100.0, health_index), 1)

        # Alarm determination
        alarm: Optional[Dict[str, Any]] = None
        if delta_p >= cls.HE_CRITICAL_DELTA_P_BAR:
            status = "CRITICAL"
            alarm = {
                "severity": "CRITICAL",
                "alarm_code": "HE_SEVERE_FOULING",
                "message": f"Critical pressure drop: {delta_p:.3f} bar exceeds limit of {cls.HE_CRITICAL_DELTA_P_BAR} bar",
                "trigger_context": {"delta_p_bar": round(delta_p, 3), "t_hot_out_c": metrics.t_hot_out_c}
            }
        elif delta_p >= 1.05:
            status = "WARNING"
            alarm = {
                "severity": "WARNING",
                "alarm_code": "HE_FOULING_INCIPIENT",
                "message": f"Elevated pressure drop: {delta_p:.3f} bar indicates scaling accumulation",
                "trigger_context": {"delta_p_bar": round(delta_p, 3), "t_hot_out_c": metrics.t_hot_out_c}
            }
        else:
            status = "NORMAL"

        return ThermodynamicKPIPayload(
            asset_id=asset_id,
            timestamp=timestamp,
            delta_t_c=round(delta_t_hot, 2),
            delta_p_bar=round(delta_p, 3),
            heat_duty_kw=round(heat_duty_kw, 2),
            health_index_pct=health_index,
            health_status=status,
            alarm_triggered=alarm
        )

    @classmethod
    def evaluate_cooling_tower(
        cls, asset_id: str, timestamp, metrics: CoolingTowerMetrics
    ) -> ThermodynamicKPIPayload:
        t_wb = calculate_stull_wet_bulb(metrics.t_ambient_db_c, metrics.relative_humidity_pct)
        approach = metrics.t_water_out_c - t_wb
        range_temp = metrics.t_water_in_c - metrics.t_water_out_c

        # Effectiveness = Range / (Range + Approach) * 100%
        denom = range_temp + approach
        effectiveness = (range_temp / denom * 100.0) if denom > 0.0 else 0.0

        # Health Index calculation based on Approach drift
        excess_approach = max(0.0, approach - cls.CT_DESIGN_APPROACH_C)
        health_index = max(0.0, 100.0 - (excess_approach / (cls.CT_CRITICAL_APPROACH_C - cls.CT_DESIGN_APPROACH_C) * 60.0))
        health_index = round(min(100.0, health_index), 1)

        alarm: Optional[Dict[str, Any]] = None
        if approach >= cls.CT_CRITICAL_APPROACH_C:
            status = "CRITICAL"
            alarm = {
                "severity": "CRITICAL",
                "alarm_code": "CT_PERFORMANCE_DEGRADED",
                "message": f"Critical Approach: {approach:.2f} C exceeds limit of {cls.CT_CRITICAL_APPROACH_C} C",
                "trigger_context": {"approach_c": round(approach, 2), "t_wb_c": round(t_wb, 2)}
            }
        elif approach >= 6.5:
            status = "WARNING"
            alarm = {
                "severity": "WARNING",
                "alarm_code": "CT_APPROACH_DRIFT",
                "message": f"Approach drift: {approach:.2f} C indicates fill fouling or reduced airflow",
                "trigger_context": {"approach_c": round(approach, 2), "t_wb_c": round(t_wb, 2)}
            }
        else:
            status = "NORMAL"

        return ThermodynamicKPIPayload(
            asset_id=asset_id,
            timestamp=timestamp,
            approach_temp_c=round(approach, 2),
            effectiveness_pct=round(effectiveness, 1),
            health_index_pct=health_index,
            health_status=status,
            alarm_triggered=alarm
        )

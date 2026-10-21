import pytest
from datetime import datetime, timezone
from ingestion.schemas.telemetry import HeatExchangerMetrics, CoolingTowerMetrics
from ingestion.kpi_engine import KPIEngine
from pydantic import ValidationError

def test_he_kpi_evaluation_normal_state():
    now = datetime.now(timezone.utc)
    metrics = HeatExchangerMetrics(
        t_hot_in_c=85.0,
        t_hot_out_c=56.0,
        t_cold_in_c=28.0,
        t_cold_out_c=42.0,
        p_in_bar=4.50,
        p_out_bar=3.80,  # Delta P = 0.70 bar (Nominal)
        flow_rate_m3h=25.0
    )
    kpi = KPIEngine.evaluate_heat_exchanger("HE-01", now, metrics)
    assert kpi.health_status == "NORMAL"
    assert kpi.health_index_pct >= 95.0
    assert kpi.alarm_triggered is None
    assert kpi.heat_duty_kw == pytest.approx(354.4, abs=5.0)

def test_he_kpi_evaluation_critical_alarm_trigger():
    now = datetime.now(timezone.utc)
    metrics = HeatExchangerMetrics(
        t_hot_in_c=85.0,
        t_hot_out_c=63.0,
        t_cold_in_c=32.0,
        t_cold_out_c=42.0,
        p_in_bar=4.50,
        p_out_bar=2.80,  # Delta P = 1.70 bar (Exceeds critical 1.40 bar)
        flow_rate_m3h=24.0
    )
    kpi = KPIEngine.evaluate_heat_exchanger("HE-01", now, metrics)
    assert kpi.health_status == "CRITICAL"
    assert kpi.health_index_pct < 50.0
    assert kpi.alarm_triggered is not None
    assert kpi.alarm_triggered["alarm_code"] == "HE_SEVERE_FOULING"

def test_pydantic_rejects_negative_pressure():
    with pytest.raises(ValidationError):
        HeatExchangerMetrics(
            t_hot_in_c=85.0,
            t_hot_out_c=56.0,
            t_cold_in_c=28.0,
            t_cold_out_c=42.0,
            p_in_bar=-5.0,  # Physically impossible pressure
            p_out_bar=3.80,
            flow_rate_m3h=25.0
        )

from datetime import datetime, timezone
from schemas.telemetry import HeatExchangerMetrics
from kpi_engine import KPIEngine
from pydantic import ValidationError

def main():
    print("=== TEST 1: VALID TELEMETRY (CLEAN HE-01) ===")
    now = datetime.now(timezone.utc)
    clean_metrics = HeatExchangerMetrics(
        t_hot_in_c=85.0,
        t_hot_out_c=56.0,
        t_cold_in_c=28.0,
        t_cold_out_c=42.0,
        p_in_bar=4.50,
        p_out_bar=3.80,  # Delta P = 0.70 bar (Clean)
        flow_rate_m3h=25.0
    )
    kpi_clean = KPIEngine.evaluate_heat_exchanger("HE-01", now, clean_metrics)
    print(f"Clean State -> Health: {kpi_clean.health_index_pct}% | Status: {kpi_clean.health_status} | "
          f"Duty: {kpi_clean.heat_duty_kw} kW | Alarm: {kpi_clean.alarm_triggered}")

    print("\n=== TEST 2: FOULED TELEMETRY (TRIGGER ALARM) ===")
    fouled_metrics = HeatExchangerMetrics(
        t_hot_in_c=85.0,
        t_hot_out_c=61.0,
        t_cold_in_c=31.0,
        t_cold_out_c=41.0,
        p_in_bar=4.50,
        p_out_bar=3.30,  # Delta P = 1.20 bar (> 1.05 Warning threshold)
        flow_rate_m3h=24.5
    )
    kpi_fouled = KPIEngine.evaluate_heat_exchanger("HE-01", now, fouled_metrics)
    print(f"Fouled State -> Health: {kpi_fouled.health_index_pct}% | Status: {kpi_fouled.health_status} | "
          f"Alarm: {kpi_fouled.alarm_triggered['alarm_code']} - {kpi_fouled.alarm_triggered['message']}")

    print("\n=== TEST 3: PYDANTIC RANGE SANITY REJECTION ===")
    try:
        # Impossible physical reading: Oil temperature at 800 Celsius
        bad_metrics = HeatExchangerMetrics(
            t_hot_in_c=800.0, # Violates le=250.0
            t_hot_out_c=56.0,
            t_cold_in_c=28.0,
            t_cold_out_c=42.0,
            p_in_bar=4.50,
            p_out_bar=3.80,
            flow_rate_m3h=25.0
        )
        print("ERROR: Pydantic failed to reject impossible temperature!")
    except ValidationError as e:
        print(f"SUCCESS: Pydantic rejected corrupted telemetry as expected: {e.errors()[0]['msg']}")

if __name__ == "__main__":
    main()

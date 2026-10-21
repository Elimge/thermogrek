import pytest
import math
from simulator.models.heat_exchanger import HeatExchangerModel
from simulator.models.cooling_tower import CoolingTowerModel

class TestHeatExchangerPhysics:
    def test_clean_state_hydraulic_baseline(self):
        """Verifies that a clean heat exchanger exhibits nominal pressure drop (~0.70 bar)."""
        he = HeatExchangerModel("HE-01")
        data = he.calculate_step(t_cold_in=28.0)
        delta_p = data["p_in_bar"] - data["p_out_bar"]
        assert delta_p == pytest.approx(0.70, abs=0.08)

    def test_fouling_increases_pressure_drop(self):
        """Verifies Darcy-Weisbach quadratic pressure drop increase under fouling."""
        he = HeatExchangerModel("HE-01")
        clean_step = he.calculate_step(t_cold_in=28.0)
        clean_dp = clean_step["p_in_bar"] - clean_step["p_out_bar"]

        he.set_fouling_factor(0.0008)  # Inject significant fouling
        fouled_step = he.calculate_step(t_cold_in=28.0)
        fouled_dp = fouled_step["p_in_bar"] - fouled_step["p_out_bar"]

        assert fouled_dp > clean_dp * 1.8  # Must increase by at least 80%

    def test_fouling_degrades_heat_duty(self):
        """Verifies that scaling reduces effective U and thermal heat duty."""
        he = HeatExchangerModel("HE-01")
        clean_data = he.calculate_step(t_cold_in=28.0)
        
        he.set_fouling_factor(0.0009)
        fouled_data = he.calculate_step(t_cold_in=28.0)

        assert fouled_data["u_effective"] < clean_data["u_effective"]
        assert fouled_data["heat_duty_kw"] < clean_data["heat_duty_kw"]
        assert fouled_data["t_hot_out_c"] > clean_data["t_hot_out_c"]  # Process fluid leaves hotter


class TestCoolingTowerPhysics:
    def test_stull_wet_bulb_known_psychrometric_point(self):
        """
        Validates Stull's equation against standardized psychrometric tables:
        At T_db = 30.0 C and RH = 60%, theoretical T_wb is ~23.95 C.
        """
        ct = CoolingTowerModel("CT-01")
        t_wb = ct.calculate_wet_bulb_temperature(t_db=30.0, rh=60.0)
        assert t_wb == pytest.approx(23.95, abs=0.35)

    def test_cooling_tower_approach_drift_under_degradation(self):
        """Verifies that fill degradation increases Approach temperature."""
        ct = CoolingTowerModel("CT-01")
        clean_step = ct.calculate_step(t_water_in=42.0, t_ambient_db=32.0, relative_humidity=65.0)
        
        ct.set_degradation_factor(0.9)  # 90% fill/nozzle degradation
        degraded_step = ct.calculate_step(t_water_in=42.0, t_ambient_db=32.0, relative_humidity=65.0)

        assert degraded_step["actual_approach_c"] > clean_step["actual_approach_c"] + 4.0
        assert degraded_step["t_water_out_c"] > clean_step["t_water_out_c"]

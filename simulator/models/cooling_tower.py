import math
import random
from typing import Dict, Any


class CoolingTowerModel:
    """
    Simulates an Induced Draft Evaporative Cooling Tower.
    Uses Stull's psychrometric equation to estimate Wet-Bulb Temperature (Twb).
    """

    def __init__(self, asset_id: str = "CT-01"):
        self.asset_id = asset_id
        self.design_approach_c = 4.5       # Nominal Approach (T_cold_out - T_wb)
        self.nominal_water_flow_m3h = 25.0
        self.fan_nominal_rpm = 1450.0

        # Degradation factor (0.0 = clean fill/nozzles, 1.0 = clogged/degraded)
        self.degradation_factor = 0.0

    @staticmethod
    def calculate_wet_bulb_temperature(t_db: float, rh: float) -> float:
        """
        Calculates Wet-Bulb Temperature (Twb) using Stull's empirical psychrometric formula.
        T_db: Dry-bulb ambient temperature in Celsius (-20 to 50 C)
        RH: Relative humidity in percent (1% to 99%)
        """
        twb = (
            t_db * math.atan(0.151977 * math.sqrt(rh + 8.313659))
            + math.atan(t_db + rh)
            - math.atan(rh - 1.676331)
            + 0.00391838 * (rh ** 1.5) * math.atan(0.023101 * rh)
            - 4.686035
        )
        return twb

    def set_degradation_factor(self, factor: float) -> None:
        """Sets tower degradation factor from 0.0 (pristine) to 1.0 (severely degraded)."""
        self.degradation_factor = max(0.0, min(1.0, factor))

    def calculate_step(
        self,
        t_water_in: float = 42.0,
        t_ambient_db: float = 32.0,
        relative_humidity: float = 65.0
    ) -> Dict[str, Any]:
        """
        Executes one cooling tower step.
        """
        # 1. Psychrometric limit
        t_wb = self.calculate_wet_bulb_temperature(t_ambient_db, relative_humidity)

        # 2. Operating Approach:
        # As fill scales or nozzles clog, Approach increases above design (loss of effectiveness)
        approach_penalty = self.degradation_factor * 6.0  # Can degrade up to +6.0 C
        actual_approach = self.design_approach_c + approach_penalty + random.gauss(0.0, 0.1)

        # Cold water return is bounded by wet bulb + approach
        t_water_out = t_wb + actual_approach

        # Guard: Water outlet cannot physically be warmer than inlet
        t_water_out = min(t_water_in - 2.0, t_water_out)

        fan_rpm = self.fan_nominal_rpm * (1.0 + random.uniform(-0.005, 0.005))
        water_flow = self.nominal_water_flow_m3h * (1.0 + random.uniform(-0.01, 0.01))

        return {
            "t_water_in_c": round(t_water_in + random.gauss(0.0, 0.1), 2),
            "t_water_out_c": round(t_water_out, 2),
            "t_ambient_db_c": round(t_ambient_db, 2),
            "relative_humidity_pct": round(relative_humidity, 1),
            "fan_speed_rpm": round(fan_rpm, 1),
            "water_flow_m3h": round(water_flow, 2),
            "t_wet_bulb_c": round(t_wb, 2),
            "actual_approach_c": round(actual_approach, 2)
        }

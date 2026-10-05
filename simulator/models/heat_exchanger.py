import math
import random
from typing import Dict, Any


class HeatExchangerModel:
    """
    Simulates a 1-Shell, 2-Tube Pass Counter-Current Heat Exchanger.
    Fluid Hot: Industrial Process Lube Oil (Cp ~ 2.0 kJ/kg*K, rho ~ 880 kg/m3)
    Fluid Cold: Cooling Water (Cp ~ 4.184 kJ/kg*K, rho ~ 1000 kg/m3)
    """

    def __init__(self, asset_id: str = "HE-01"):
        self.asset_id = asset_id

        # Nominal Design Parameters
        self.nominal_flow_m3h = 25.0
        self.nominal_p_in_bar = 4.50
        self.clean_delta_p_bar = 0.70
        self.heat_transfer_area_m2 = 18.5  # Transfer Area (A)
        self.u_clean = 450.0               # Clean Overall Heat Transfer Coeff (W/m2*K)

        # Operational Boundaries
        self.t_hot_in_nominal = 85.0       # Process Oil Inlet Temp (C)
        self.t_cold_in_nominal = 28.0      # Cooling Water Return Temp (C)

        # Degradation state (Fouling resistance Rf in m2*K/W)
        self.rf = 0.0

    def set_fouling_factor(self, rf: float) -> None:
        """Sets the fouling resistance Rf (0.0 = clean, > 0.0008 = critical)."""
        self.rf = max(0.0, rf)

    def calculate_step(self, t_cold_in: float = 28.0) -> Dict[str, Any]:
        """
        Executes one thermodynamic & hydraulic simulation step.
        """
        # 1. Effective Overall Heat Transfer Coefficient U(t)
        # 1/U = 1/U_clean + Rf
        u_effective = 1.0 / ((1.0 / self.u_clean) + self.rf)

        # 2. Add realistic operational flow fluctuations (+- 1.5%)
        flow_rate_m3h = self.nominal_flow_m3h * (1.0 + random.uniform(-0.015, 0.015))

        # 3. Hydraulic Pressure Drop calculation:
        # Scaling reduces tube effective diameter, increasing Delta P quadratically.
        # Fouling penalty factor proportional to Rf
        fouling_hydraulic_factor = 1.0 + (self.rf * 1800.0)
        flow_ratio = flow_rate_m3h / self.nominal_flow_m3h
        delta_p = self.clean_delta_p_bar * fouling_hydraulic_factor * (flow_ratio ** 2)

        # Sensor readings for Pressure with small sensor noise
        p_in = self.nominal_p_in_bar + random.gauss(0.0, 0.01)
        p_out = p_in - delta_p + random.gauss(0.0, 0.01)

        # 4. Thermal behavior under fouling:
        # As U decays, heat duty drops, meaning hot stream cools LESS and cold stream heats LESS.
        cleanliness_ratio = u_effective / self.u_clean
        nominal_heat_duty_kw = 350.0
        actual_heat_duty_kw = nominal_heat_duty_kw * (0.55 + 0.45 * cleanliness_ratio)

        # Oil side: m_dot * Cp * delta_T -> calculate T_hot_out
        oil_mass_flow_kgs = (flow_rate_m3h * 880.0) / 3600.0  # kg/s
        cp_oil = 2.0  # kJ/kg*K
        delta_t_hot = actual_heat_duty_kw / (oil_mass_flow_kgs * cp_oil)

        # Water side: m_dot * Cp * delta_T -> calculate T_cold_out
        water_mass_flow_kgs = (flow_rate_m3h * 1000.0) / 3600.0  # kg/s
        cp_water = 4.184  # kJ/kg*K
        delta_t_cold = actual_heat_duty_kw / (water_mass_flow_kgs * cp_water)

        t_hot_in = self.t_hot_in_nominal + random.gauss(0.0, 0.15)
        t_hot_out = t_hot_in - delta_t_hot + random.gauss(0.0, 0.15)
        t_cold_out = t_cold_in + delta_t_cold + random.gauss(0.0, 0.15)

        return {
            "t_hot_in_c": round(t_hot_in, 2),
            "t_hot_out_c": round(t_hot_out, 2),
            "t_cold_in_c": round(t_cold_in, 2),
            "t_cold_out_c": round(t_cold_out, 2),
            "p_in_bar": round(p_in, 3),
            "p_out_bar": round(p_out, 3),
            "flow_rate_m3h": round(flow_rate_m3h, 2),
            "u_effective": round(u_effective, 2),
            "heat_duty_kw": round(actual_heat_duty_kw, 2)
        }
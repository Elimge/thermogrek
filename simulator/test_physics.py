from models.heat_exchanger import HeatExchangerModel
from models.cooling_tower import CoolingTowerModel

def main():
    print("=== TESTING HEAT EXCHANGER (HE-01) ===")
    he = HeatExchangerModel()
    
    # State 1: Clean
    clean_step = he.calculate_step(t_cold_in=28.0)
    print(f"Clean HE: Delta_P = {clean_step['p_in_bar'] - clean_step['p_out_bar']:.3f} bar | "
          f"T_hot_out = {clean_step['t_hot_out_c']} C | Duty = {clean_step['heat_duty_kw']} kW")

    # State 2: Critical Fouling (Rf = 0.0009)
    he.set_fouling_factor(0.0009)
    fouled_step = he.calculate_step(t_cold_in=28.0)
    print(f"Fouled HE: Delta_P = {fouled_step['p_in_bar'] - fouled_step['p_out_bar']:.3f} bar | "
          f"T_hot_out = {fouled_step['t_hot_out_c']} C | Duty = {fouled_step['heat_duty_kw']} kW")

    print("\n=== TESTING COOLING TOWER (CT-01) ===")
    ct = CoolingTowerModel()
    
    # State 1: Clean
    ct_clean = ct.calculate_step(t_water_in=42.0, t_ambient_db=32.0, relative_humidity=65.0)
    print(f"Clean CT: Twb = {ct_clean['t_wet_bulb_c']} C | Approach = {ct_clean['actual_approach_c']} C | "
          f"T_water_out = {ct_clean['t_water_out_c']} C")

    # State 2: Degraded (factor = 0.8)
    ct.set_degradation_factor(0.8)
    ct_degraded = ct.calculate_step(t_water_in=42.0, t_ambient_db=32.0, relative_humidity=65.0)
    print(f"Degraded CT: Twb = {ct_degraded['t_wet_bulb_c']} C | Approach = {ct_degraded['actual_approach_c']} C | "
          f"T_water_out = {ct_degraded['t_water_out_c']} C")

if __name__ == "__main__":
    main()

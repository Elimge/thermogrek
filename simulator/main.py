import time
import signal
import sys
import logging
from config import SimulatorConfig
from publisher import MQTTPublisher
from models.heat_exchanger import HeatExchangerModel
from models.cooling_tower import CoolingTowerModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ThermoGrekSimulator")

running = True

def handle_shutdown(signum, frame):
    global running
    logger.info("Received termination signal (%d). Shutting down simulation...", signum)
    running = False

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

def main():
    logger.info("Starting ThermoGrek Industrial Plant Simulator...")
    
    cfg = SimulatorConfig()
    publisher = MQTTPublisher(cfg.MQTT_HOST, cfg.MQTT_PORT, cfg.MQTT_KEEPALIVE)
    publisher.setup_lwt(cfg.PLANT_ID)
    publisher.connect()

    he = HeatExchangerModel("HE-01")
    ct = CoolingTowerModel("CT-01")

    simulated_day = 1.0

    try:
        while running:
            # Advance simulated operational degradation
            simulated_day += cfg.DEGRADATION_RATE_DAYS_PER_SEC
            
            # Map simulated days to Fouling Factor Rf
            # From Day 1 to Day 80, Rf rises from 0.0 to 0.00095 m2*K/W
            rf = max(0.0, (simulated_day - 15.0) * 0.000015) if simulated_day > 15.0 else 0.0
            he.set_fouling_factor(rf)

            # Cooling tower degradation slowly increases after Day 30
            ct_degradation = min(1.0, max(0.0, (simulated_day - 30.0) / 70.0))
            ct.set_degradation_factor(ct_degradation)

            # Step 1: Run cooling tower
            ct_data = ct.calculate_step(
                t_water_in=42.0,
                t_ambient_db=31.5,
                relative_humidity=62.0
            )

            # Step 2: Heat exchanger uses cooled water from tower as its cold inlet!
            he_data = he.calculate_step(t_cold_in=ct_data["t_water_out_c"])

            # Step 3: Publish telemetry to MQTT broker
            publisher.publish_telemetry(cfg.PLANT_ID, "HE-01", he_data)
            publisher.publish_telemetry(cfg.PLANT_ID, "CT-01", ct_data)

            if int(simulated_day) % 5 == 0 and abs(simulated_day - round(simulated_day)) < cfg.DEGRADATION_RATE_DAYS_PER_SEC:
                logger.info(
                    "Simulated Day: %.1f | HE Delta_P: %.3f bar | HE T_out: %.2f C | CT Approach: %.2f C",
                    simulated_day,
                    he_data["p_in_bar"] - he_data["p_out_bar"],
                    he_data["t_hot_out_c"],
                    ct_data["actual_approach_c"]
                )

            time.sleep(cfg.PUBLISH_INTERVAL_SEC)

    finally:
        publisher.disconnect()
        logger.info("Simulator terminated safely.")

if __name__ == "__main__":
    main()

import os

class SimulatorConfig:
    # MQTT Broker connection settings
    MQTT_HOST: str = os.getenv("MQTT_HOST", "mqtt-broker")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", 1883))
    MQTT_KEEPALIVE: int = int(os.getenv("MQTT_KEEPALIVE", 60))

    # Simulation loop settings
    PUBLISH_INTERVAL_SEC: float = float(os.getenv("PUBLISH_INTERVAL_SEC", 1.0))
    PLANT_ID: str = os.getenv("PLANT_ID", "main")

    # Degradation acceleration (operational days advanced per real second)
    # Default: 0.05 days/sec means 20 seconds = 1 operational day
    DEGRADATION_RATE_DAYS_PER_SEC: float = float(os.getenv("DEGRADATION_RATE", 0.05))

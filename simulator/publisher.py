import json
import logging
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger("SimulatorPublisher")

class MQTTPublisher:
    def __init__(self, host: str, port: int, keepalive: int = 60):
        self.host = host
        self.port = port
        self.keepalive = keepalive
        
        # Use modern CallbackAPIVersion.VERSION2 for paho-mqtt >= 2.0
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="thermogrek-edge-simulator"
        )
        
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Successfully connected to MQTT Broker at %s:%d", self.host, self.port)
            # Announce online state for both assets
            self.publish_status("HE-01", "ONLINE")
            self.publish_status("CT-01", "ONLINE")
        else:
            logger.error("Failed to connect to MQTT Broker, return code: %d", rc)

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        logger.warning("Disconnected from MQTT Broker with return code: %d", rc)

    def setup_lwt(self, plant_id: str):
        """Sets up Last Will and Testament so broker marks assets OFFLINE if simulator crashes."""
        lwt_payload = json.dumps({
            "status": "OFFLINE",
            "reason": "SIMULATOR_UNEXPECTED_TERMINATION",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.client.will_set(
            topic=f"thermogrek/plants/{plant_id}/system/status",
            payload=lwt_payload,
            qos=1,
            retain=True
        )

    def connect(self):
        logger.info("Connecting to MQTT Broker at %s:%d...", self.host, self.port)
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.loop_start()

    def disconnect(self):
        logger.info("Disconnecting cleanly from MQTT Broker...")
        self.publish_status("HE-01", "OFFLINE")
        self.publish_status("CT-01", "OFFLINE")
        self.client.loop_stop()
        self.client.disconnect()

    def publish_status(self, asset_id: str, status: str):
        topic = f"thermogrek/plants/main/assets/{asset_id}/status"
        payload = json.dumps({
            "asset_id": asset_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.client.publish(topic, payload, qos=1, retain=True)

    def publish_telemetry(self, plant_id: str, asset_id: str, metrics: Dict[str, Any]):
        topic = f"thermogrek/plants/{plant_id}/assets/{asset_id}/telemetry"
        payload = json.dumps({
            "asset_id": asset_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
            "operational_mode": "NORMAL"
        })
        self.client.publish(topic, payload, qos=1, retain=False)

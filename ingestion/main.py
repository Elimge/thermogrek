import json
import signal
import sys
import logging
import paho.mqtt.client as mqtt
from config import IngestionConfig
from db_repository import DatabaseRepository
from schemas.telemetry import TelemetryEnvelope, HeatExchangerMetrics, CoolingTowerMetrics
from kpi_engine import KPIEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("IngestionService")

running = True
cfg = IngestionConfig()
repo = DatabaseRepository(cfg.db_conn_info)

def handle_shutdown(signum, frame):
    global running
    logger.info("Received termination signal (%d). Shutting down ingestion service...", signum)
    running = False

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Connected to MQTT Broker. Subscribing to: %s", cfg.MQTT_TOPIC_SUB)
        client.subscribe(cfg.MQTT_TOPIC_SUB, qos=1)
    else:
        logger.error("Failed to connect to MQTT broker, code: %d", rc)

def on_message(client, userdata, msg):
    try:
        raw_payload = json.loads(msg.payload.decode("utf-8"))
        envelope = TelemetryEnvelope(**raw_payload)
        
        # Dispatch to thermodynamic evaluation depending on asset type
        if envelope.asset_id == "HE-01":
            metrics = HeatExchangerMetrics(**envelope.metrics)
            kpi = KPIEngine.evaluate_heat_exchanger(envelope.asset_id, envelope.timestamp, metrics)
        elif envelope.asset_id == "CT-01":
            metrics = CoolingTowerMetrics(**envelope.metrics)
            kpi = KPIEngine.evaluate_cooling_tower(envelope.asset_id, envelope.timestamp, metrics)
        else:
            logger.warning("Unrecognized asset ID: %s", envelope.asset_id)
            return

        # Persist everything in PostgreSQL
        repo.save_reading_and_kpis(envelope, kpi)

        # Broadcast calculated KPIs to MQTT for downstream WebSocket API
        kpi_topic = f"thermogrek/plants/main/assets/{envelope.asset_id}/kpis"
        client.publish(kpi_topic, kpi.model_dump_json(), qos=1)

        if kpi.alarm_triggered:
            logger.warning("ALARM TRIGGERED on %s: %s", envelope.asset_id, kpi.alarm_triggered["message"])

    except Exception as e:
        logger.error("Error processing MQTT message on %s: %s", msg.topic, e, exc_info=True)

def main():
    logger.info("Starting ThermoGrek IoT Ingestion Service...")
    repo.open()

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="thermogrek-ingestion-worker"
    )
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(cfg.MQTT_HOST, cfg.MQTT_PORT, 60)
        client.loop_start()

        while running:
            signal.pause() if hasattr(signal, "pause") else sys.stdin.read()

    finally:
        client.loop_stop()
        client.disconnect()
        repo.close()
        logger.info("Ingestion service terminated cleanly.")

if __name__ == "__main__":
    main()

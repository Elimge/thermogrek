import os

class IngestionConfig:
    MQTT_HOST: str = os.getenv("MQTT_HOST", "mqtt-broker")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", 1883))
    MQTT_TOPIC_SUB: str = os.getenv("MQTT_TOPIC_SUB", "thermogrek/plants/+/assets/+/telemetry")

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "database")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "thermogrek_db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "thermogrek_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "thermogrek_dev_pass_secure_2026")

    @property
    def db_conn_info(self) -> str:
        return (
            f"host={self.POSTGRES_HOST} port={self.POSTGRES_PORT} "
            f"dbname={self.POSTGRES_DB} user={self.POSTGRES_USER} "
            f"password={self.POSTGRES_PASSWORD}"
        )

import json
import logging
from psycopg_pool import ConnectionPool
from schemas.telemetry import TelemetryEnvelope
from schemas.kpi import ThermodynamicKPIPayload

logger = logging.getLogger("DatabaseRepository")

class DatabaseRepository:
    def __init__(self, conn_info: str):
        self.pool = ConnectionPool(
            conninfo=conn_info,
            min_size=2,
            max_size=10,
            timeout=10.0
        )

    def open(self):
        self.pool.open()
        logger.info("Database Connection Pool successfully opened.")

    def close(self):
        self.pool.close()
        logger.info("Database Connection Pool closed.")

    def save_reading_and_kpis(
        self,
        envelope: TelemetryEnvelope,
        kpi: ThermodynamicKPIPayload
    ):
        with self.pool.connection() as conn:
            with conn.transaction():
                # 1. Insert Raw Telemetry
                conn.execute(
                    """
                    INSERT INTO telemetry_readings (timestamp, asset_id, metrics)
                    VALUES (%s, %s, %s);
                    """,
                    (envelope.timestamp, envelope.asset_id, json.dumps(envelope.metrics))
                )

                # 2. Insert Calculated KPIs
                conn.execute(
                    """
                    INSERT INTO thermodynamic_kpis (
                        timestamp, asset_id, delta_t_c, delta_p_bar, heat_duty_kw,
                        approach_temp_c, effectiveness_pct, health_index_pct
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        kpi.timestamp,
                        kpi.asset_id,
                        kpi.delta_t_c,
                        kpi.delta_p_bar,
                        kpi.heat_duty_kw,
                        kpi.approach_temp_c,
                        kpi.effectiveness_pct,
                        kpi.health_index_pct
                    )
                )

                # 3. Update Asset Health Status
                conn.execute(
                    """
                    UPDATE assets
                    SET health_status = %s, updated_at = NOW()
                    WHERE id = %s;
                    """,
                    (kpi.health_status, envelope.asset_id)
                )

                # 4. Insert Alarm if triggered
                if kpi.alarm_triggered:
                    conn.execute(
                        """
                        INSERT INTO alarms (
                            triggered_at, asset_id, severity, alarm_code, message, trigger_context
                        )
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """,
                        (
                            kpi.timestamp,
                            envelope.asset_id,
                            kpi.alarm_triggered["severity"],
                            kpi.alarm_triggered["alarm_code"],
                            kpi.alarm_triggered["message"],
                            json.dumps(kpi.alarm_triggered["trigger_context"])
                        )
                    )

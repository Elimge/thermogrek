from typing import List, Optional, Dict, Any
from datetime import datetime
from psycopg import AsyncConnection
from psycopg.rows import dict_row

class TelemetryRepository:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def get_latest_reading_and_kpis(self, asset_id: str) -> Optional[Dict[str, Any]]:
        async with self.conn.cursor(row_factory=dict_row) as cur:
            # Query latest telemetry reading
            await cur.execute(
                """
                SELECT timestamp, metrics
                FROM telemetry_readings
                WHERE asset_id = %s
                ORDER BY timestamp DESC
                LIMIT 1;
                """,
                (asset_id,)
            )
            telemetry = await cur.fetchone()

            if not telemetry:
                return None

            # Query latest KPI
            await cur.execute(
                """
                SELECT delta_t_c, delta_p_bar, heat_duty_kw, approach_temp_c, effectiveness_pct, health_index_pct
                FROM thermodynamic_kpis
                WHERE asset_id = %s
                ORDER BY timestamp DESC
                LIMIT 1;
                """,
                (asset_id,)
            )
            kpi = await cur.fetchone() or {}

            # Query asset current health status
            await cur.execute(
                "SELECT health_status FROM assets WHERE id = %s;",
                (asset_id,)
            )
            asset = await cur.fetchone() or {"health_status": "NORMAL"}

            return {
                "asset_id": asset_id,
                "timestamp": telemetry["timestamp"],
                "metrics": telemetry["metrics"],
                "kpis": kpi,
                "health_status": asset["health_status"]
            }

    async def get_historical_telemetry(
        self, asset_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Returns recent historical readings ordered chronologically for frontend charts."""
        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT timestamp, metrics
                FROM (
                    SELECT timestamp, metrics
                    FROM telemetry_readings
                    WHERE asset_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                ) sub
                ORDER BY timestamp ASC;
                """,
                (asset_id, limit)
            )
            return await cur.fetchall()

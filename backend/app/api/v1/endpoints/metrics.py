from fastapi import APIRouter, Depends
from psycopg import AsyncConnection
from app.db.session import get_db_connection, db_pool
from app.websocket.manager import ws_manager

router = APIRouter()

@router.get("/metrics", tags=["Observability"])
async def get_system_metrics(conn: AsyncConnection = Depends(get_db_connection)):
    """Returns real-time operational and platform metrics."""
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT 
                (SELECT COUNT(*) FROM telemetry_readings) AS total_readings,
                (SELECT COUNT(*) FROM thermodynamic_kpis) AS total_kpis,
                (SELECT COUNT(*) FROM alarms WHERE acknowledged = FALSE) AS active_alarms,
                (SELECT COUNT(*) FROM assets WHERE is_active = TRUE) AS active_assets;
            """
        )
        row = await cur.fetchone()

    return {
        "telemetry_pipeline": {
            "total_readings_persisted": row[0],
            "total_kpis_calculated": row[1],
            "active_assets_monitored": row[3]
        },
        "alarm_system": {
            "active_unacknowledged_alarms": row[2]
        },
        "realtime_streaming": {
            "connected_websocket_clients": len(ws_manager.active_connections)
        },
        "persistence_pool": {
            "min_connections": db_pool.min_size,
            "max_connections": db_pool.max_size
        }
    }

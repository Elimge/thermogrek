from typing import List
from psycopg import AsyncConnection
from psycopg.rows import dict_row

class AlarmRepository:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def get_active_alarms(self) -> List[dict]:
        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT id::text, triggered_at, cleared_at, asset_id, severity, alarm_code, message, trigger_context, acknowledged
                FROM alarms
                WHERE acknowledged = FALSE
                ORDER BY triggered_at DESC;
                """
            )
            return await cur.fetchall()

    async def acknowledge_alarm(self, alarm_id: str) -> bool:
        async with self.conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE alarms
                SET acknowledged = TRUE
                WHERE id = %s::uuid;
                """,
                (alarm_id,)
            )
            return cur.rowcount > 0

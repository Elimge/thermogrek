from typing import List, Optional
from psycopg import AsyncConnection
from psycopg.rows import dict_row

class AssetRepository:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def get_all_active(self) -> List[dict]:
        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT id, plant_id::text, name, asset_type, health_status, is_active, created_at
                FROM assets
                WHERE is_active = TRUE
                ORDER BY id;
                """
            )
            return await cur.fetchall()

    async def get_by_id(self, asset_id: str) -> Optional[dict]:
        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT id, plant_id::text, name, asset_type, health_status, is_active, design_parameters, created_at
                FROM assets
                WHERE id = %s AND is_active = TRUE;
                """,
                (asset_id,)
            )
            return await cur.fetchone()

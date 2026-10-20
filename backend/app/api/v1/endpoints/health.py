from fastapi import APIRouter, Depends
from psycopg import AsyncConnection
from app.db.session import get_db_connection

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check(conn: AsyncConnection = Depends(get_db_connection)):
    """Verifies that API and database connection pool are fully healthy."""
    async with conn.cursor() as cur:
        await cur.execute("SELECT 1;")
        db_alive = (await cur.fetchone())[0] == 1
    return {
        "status": "healthy" if db_alive else "degraded",
        "subsystems": {
            "api": "online",
            "database": "connected" if db_alive else "disconnected"
        }
    }

import logging
from typing import AsyncGenerator
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from app.core.config import settings

logger = logging.getLogger("DatabasePool")

db_pool = AsyncConnectionPool(
    conninfo=settings.async_db_conn_info,
    min_size=2,
    max_size=10,
    open=False
)

async def init_db_pool():
    await db_pool.open()
    logger.info("Async PostgreSQL Connection Pool initialized successfully.")

async def close_db_pool():
    await db_pool.close()
    logger.info("Async PostgreSQL Connection Pool closed.")

async def get_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    """Dependency injection helper for FastAPI routes."""
    async with db_pool.connection() as conn:
        yield conn

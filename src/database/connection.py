
import asyncpg
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages the connection to the PostgreSQL database using asyncpg.
    """
    def __init__(self, db_url: str):
        self._db_url = db_url
        self._pool: asyncpg.Pool | None = None

    async def connect(self):
        """
        Establishes the database connection pool.
        Should be called on application startup.
        """
        if not self._pool:
            try:
                self._pool = await asyncpg.create_pool(self._db_url)
                logger.info("Database connection pool established.")
            except Exception as e:
                logger.critical(f"Failed to connect to the database: {e}", exc_info=True)
                raise

    async def disconnect(self):
        """
        Closes the database connection pool.
        Should be called on application shutdown.
        """
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed.")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Provides a connection from the pool within a context manager.
        Ensures the connection is released back to the pool.
        """
        if not self._pool:
            raise ConnectionError("Database pool is not initialized. Call connect() first.")
        
        async with self._pool.acquire() as connection:
            yield connection

    async def init_db(self):
        """
        Initializes the database schema by creating necessary tables.
        """
        logger.info("Initializing database schema...")
        async with self.get_connection() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    role VARCHAR(10) NOT NULL DEFAULT 'free',
                    points INTEGER NOT NULL DEFAULT 0
                );
            """)
            # You can add more table creations here
        logger.info("Database schema initialized successfully.")


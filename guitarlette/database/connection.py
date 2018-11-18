from typing import Callable
from contextlib import asynccontextmanager
import asyncpg


@asynccontextmanager
async def get_connection(pool):

    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)


class Connection:
    def __init__(self, db_config: dict) -> None:
        self.db_config = db_config
        self.conn = {"pool": None}

    async def get_pool(self):
        if self.conn["pool"] is None:
            await self.create_connection()
        return self.conn["pool"]

    async def create_connection(self) -> None:

        self.conn["pool"] = await asyncpg.create_pool(**self.db_config)

    async def close_connection(self) -> None:
        await self.conn["pool"].close()

    async def perform(self, query: Callable):

        pool = await self.get_pool()

        async with get_connection(pool) as conn:
            async with conn.transaction():
                res = await query(conn)
        return res

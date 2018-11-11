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
    def __init__(self, database: str) -> None:
        self.database = database
        self.config = {"pool": None}

    async def get_pool(self):
        if self.config["pool"] is None:
            await self.create_connection()
        return self.config["pool"]

    async def create_connection(self) -> None:

        self.config["pool"] = await asyncpg.create_pool(database=self.database)

    async def close_connection(self) -> None:
        await self.config["pool"].close()

    async def perform(self, query: Callable):

        pool = await self.get_pool()

        async with get_connection(pool) as conn:
            async with conn.transaction():
                res = await query(conn)
        return res

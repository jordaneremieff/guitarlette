import asyncio
import asyncpg

from guitarlette.config import DB_CONFIG


async def main():
    conn = await asyncpg.connect(
        f"postgresql://postgres@localhost/{DB_CONFIG['database']}",
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    await conn.execute(
        """
        CREATE TABLE song(
            "id" int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "name" varchar(100) NOT NULL,
            "content" text NULL
        );
        """
    )
    await conn.close()


asyncio.run(main())

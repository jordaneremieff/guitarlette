import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect("postgresql://postgres@localhost/guitarlette")
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

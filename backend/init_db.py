import asyncio
from databases import Database


async def main() -> None:
    database = Database("sqlite:///guitarlette.db")
    await database.connect()
    query = """CREATE TABLE Songs (id INTEGER PRIMARY KEY, title VARCHAR(100), content TEXT)"""
    await database.execute(query=query)
    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

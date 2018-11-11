from typing import Union
from dataclasses import dataclass
from guitarlette.database.connection import Connection


@dataclass
class Song:

    id: int
    name: str = None
    content: str = None


@dataclass
class SongQuery:

    db: Connection
    model: Song = Song

    @property
    def select_columns(self) -> str:
        return """id, name, content"""

    def get_queryset(self, res, many=False) -> Union[Song, None]:
        if not res:
            return None

        if many:

            return [self.serialize(row) for row in res]

        return self.serialize(res)

    def serialize(self, row):
        return self.model(**dict(row))

    async def get(self, id: int) -> Song:
        statement = f"""
        SELECT {self.select_columns}
        FROM song
        WHERE song.id = $1
        """
        res = await self.db.perform(lambda conn: conn.fetchrow(statement, id))
        return self.get_queryset(res)

    async def list(self) -> Song:
        statement = f"""
        SELECT {self.select_columns}
        FROM song
        """
        res = await self.db.perform(lambda conn: conn.fetch(statement))
        return self.get_queryset(res, many=True)

    async def create(self, name, content: str = None) -> Song:
        statement = """
        INSERT INTO song
        VALUES(DEFAULT, $1, $2)
        RETURNING id, name, content
        """
        res = await self.db.perform(
            lambda conn: conn.fetchrow(statement, name, content)
        )
        return self.get_queryset(res)

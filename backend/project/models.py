import typing

import databases
import orm
import sqlalchemy

from .utils import get_db_url
from .parser import Parser

database = databases.Database(get_db_url())
metadata = sqlalchemy.MetaData()


class Artist(orm.Model):

    __tablename__ = "artists"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    name = orm.String(max_length=255, unique=True)


class Song(orm.Model):
    __tablename__ = "songs"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    title = orm.String(max_length=255)
    artist = orm.ForeignKey(Artist)
    content = orm.Text(allow_null=True)

    async def get_dict(self, new: bool = False) -> typing.Dict:
        await self.artist.load()
        html = Parser(self.content).html
        data = {
            "id": self.id,
            "title": self.title,
            "artist": self.artist.name,
            "content": self.content,
            "html": html,
        }
        data["type"] = "song.detail" if not new else "song.created"
        return data


class User(orm.Model):

    __tablename__ = "users"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    name = orm.String(max_length=255)
    email = orm.String(max_length=255, unique=True)
    password = orm.String(max_length=255)

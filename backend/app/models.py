import typing

import databases
import orm
import sqlalchemy


from .parser import Parser

database = databases.Database("sqlite:///guitarlette.db")
metadata = sqlalchemy.MetaData()


class Song(orm.Model):
    __tablename__ = "songs"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    title = orm.String(max_length=100)
    artist = orm.String(max_length=100)
    content = orm.Text(allow_null=True)

    def get_dict(self, created: bool = False) -> typing.Dict:
        html = Parser(self.content).html
        data = {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "content": self.content,
            "viewer_content": html,
        }
        if created:
            data["redirect"] = True
        return data

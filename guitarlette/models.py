from tortoise.models import Model
from tortoise import fields

from guitarlette.parser import SongParser


class Artist(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()


class Revision(Model):
    """
    A previous version of a saved song.
    """

    id = fields.IntField(pk=True)
    song = fields.ForeignKeyField("models.Song", related_name="revisions")
    # artist = fields.ForeignKeyField("models.Artist")
    title = fields.TextField()
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Song(Model):
    """
    A song saved in the composer.

    May have many revisions and optionally belong to a single notebook.
    """

    DRAFT = 0
    PUBLISHED = 1

    id = fields.IntField(pk=True)
    notebook = fields.ForeignKeyField(
        "models.Notebook", null=True, related_name="songs", on_delete=fields.SET_NULL
    )
    # artist = fields.ForeignKeyField("models.Artist")
    title = fields.TextField()
    content = fields.TextField()
    status = fields.IntField(default=DRAFT)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    @property
    def parser(self) -> SongParser:
        return SongParser(self.content)

    @property
    def chords(self):
        return self.parser.chords

    @property
    def html(self) -> str:
        return self.parser.html

    @property
    def json(self) -> str:
        return self.parser.json


class Notebook(Model):
    """
    A collection of songs.
    """

    id = fields.IntField(pk=True)
    title = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

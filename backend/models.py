from tortoise.models import Model
from tortoise import fields

from guitarlette.parser import Parser


class Revision(Model):
    """
    A previous version of a saved song.
    """

    id = fields.IntField(pk=True)
    song = fields.ForeignKeyField("models.Song", related_name="revisions")
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
    artist = fields.TextField(default="nobody")
    title = fields.TextField()
    content = fields.TextField()
    status = fields.IntField(default=DRAFT)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    @property
    def parser(self) -> Parser:
        return Parser(self.content)

    @property
    def chords(self):
        return self.parser.chords

    @property
    def html(self) -> str:
        return self.parser.html

from tortoise.models import Model
from tortoise import fields


class Song(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    content = fields.TextField()
    # notebook = fields.ForeignKeyField("models.Notebook", related_name="songs")

    def __str__(self):
        return self.name


class Notebook(Model):

    id = fields.IntField(pk=True)
    name = fields.TextField()

    def __str__(self):
        return self.name

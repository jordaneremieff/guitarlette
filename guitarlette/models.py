from tortoise.models import Model
from tortoise import fields


class Revision(Model):
    id = fields.IntField(pk=True)
    song = fields.ForeignKeyField("models.Song", related_name="revisions")
    name = fields.TextField()
    content = fields.TextField()

    def __str__(self):
        return self.name


class Song(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    content = fields.TextField()
    # notebook = fields.ForeignKeyField(
    #     "models.Notebook", related_name="songs", null=True
    # )

    def __str__(self):
        return self.name


# class Notebook(Model):
#     id = fields.IntField(pk=True)
#     name = fields.TextField()

#     def __str__(self):
#         return self.name

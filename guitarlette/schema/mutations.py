import graphene

from guitarlette.models import Song
from guitarlette.schema.types import SongType


class CreateSongMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        content = graphene.String()

    song = graphene.Field(SongType)

    async def mutate(self, info, name, content):
        song = await Song.create(name=name, content=content)
        return CreateSongMutation(song=song)


class UpdateSongMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        name = graphene.String()

    song = graphene.Field(SongType)

    async def mutate(self, info, id, name):
        song = await Song.update(id=id, name=name)
        return UpdateSongMutation(song=song)


class Mutation(graphene.ObjectType):
    create_song = CreateSongMutation.Field()
    update_song = UpdateSongMutation.Field()

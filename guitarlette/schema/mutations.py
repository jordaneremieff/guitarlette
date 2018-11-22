import graphene

from guitarlette.models import Song
from guitarlette.schema.types import SongType


class CreateSongMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        content = graphene.String(required=True)

    song = graphene.Field(SongType)

    async def mutate(self, info, name: str, content: str):
        song = await Song.create(name=name, content=content)
        return CreateSongMutation(song=song)


class UpdateSongMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        content = graphene.String()

    song = graphene.Field(SongType)

    async def mutate(self, info, id: int, name: str = None, content: str = None):
        song = await Song.get(id=id)

        if name is not None:
            song.name = name
        if content is not None:
            song.content = content

        await song.save()

        return UpdateSongMutation(song=song)


class Mutation(graphene.ObjectType):
    create_song = CreateSongMutation.Field()
    update_song = UpdateSongMutation.Field()

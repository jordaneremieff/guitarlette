import graphene

from guitarlette.models import Song  # , Notebook
from guitarlette.schema.types import SongType
from guitarlette.schema.mutations import Mutation


class Query(graphene.ObjectType):

    all_songs = graphene.List(SongType)
    song = graphene.Field(SongType, id=graphene.Int())

    async def resolve_all_songs(self, info):
        songs = await Song.all()
        return songs

    async def resolve_song(self, info, id):
        song = await Song.get(id=id)
        return song


schema = graphene.Schema(query=Query, mutation=Mutation)

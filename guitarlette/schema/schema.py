import graphene

from guitarlette.database.connection import Connection
from guitarlette.database.models import SongQuery
from guitarlette.config import DB_CONFIG

db = Connection(db_config=DB_CONFIG)


class SongType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    content = graphene.String()


class CreateSongMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        content = graphene.String()

    song = graphene.Field(SongType)

    async def mutate(self, info, name, content):
        song = await SongQuery(db).create(name=name, content=content)
        return CreateSongMutation(song=song)


class UpdateSongMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        name = graphene.String()

    song = graphene.Field(SongType)

    async def mutate(self, info, id, name):
        song = await SongQuery(db).update(id=id, name=name)
        return UpdateSongMutation(song=song)


class Mutation(graphene.ObjectType):
    create_song = CreateSongMutation.Field()
    update_song = UpdateSongMutation.Field()


class Query(graphene.ObjectType):

    all_songs = graphene.List(SongType)
    song = graphene.Field(SongType, id=graphene.Int())

    async def resolve_all_songs(self, info):
        songs = await SongQuery(db).list()
        return songs

    async def resolve_song(self, info, id):
        song = await SongQuery(db).get(id=id)
        return song


schema = graphene.Schema(query=Query, mutation=Mutation)

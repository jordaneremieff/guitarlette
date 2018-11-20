import graphene


class SongType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    content = graphene.String()

import typing

from starlette.endpoints import WebSocketEndpoint
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from orm.exceptions import NoMatch

from .schema import SongSchema
from .models import database, Song, Artist
from .parser import Parser


app = Starlette()
app.debug = True


@app.route("/songs")
async def get_songs(request) -> JSONResponse:
    songs = await Song.objects.select_related("artist").all()
    return JSONResponse(
        [
            {"id": song.id, "title": song.title, "artist": song.artist.name}
            for song in songs
        ]
    )


@app.route("/artists")
async def get_artists(request) -> JSONResponse:
    artists = await Artist.objects.all()
    return JSONResponse([{"name": artist.name} for artist in artists])


@app.websocket_route("/ws")
class ComposerEndpoint(WebSocketEndpoint):

    encoding = "json"

    async def on_receive(self, websocket, message: typing.Dict) -> None:
        _type, _method = message.pop("type").split(".")
        method = f"{_method}_{_type}"
        response = await getattr(self, method)(message)
        await websocket.send_json(response)

    async def create_song(self, message: typing.Dict) -> typing.Dict:
        _, errors = SongSchema.validate_or_error(message)
        if errors:
            return {"type": "song.errors", "detail": dict(errors)}
        artist_obj = await Artist.objects.get(name=message["artist"])
        song_obj = await Song.objects.create(
            title=message["title"], content=message["content"], artist=artist_obj
        )
        song_dict = await song_obj.get_dict(new=True)
        return song_dict

    async def get_song(self, message: typing.Dict) -> typing.Dict:
        id = int(message.pop("id"))
        try:
            song = await Song.objects.select_related("artist").get(id=id)
        except NoMatch:
            return {"type": "song.missing", "detail": "Song not found"}
        song_dict = await song.get_dict()
        return song_dict

    async def update_song(self, message: typing.Dict) -> typing.Dict:
        id = int(message.pop("id"))
        try:
            song = await Song.objects.get(id=id)
        except NoMatch:
            return {"type": "song.missing", "detail": "Song not found"}
        _, errors = SongSchema.validate_or_error(message)
        if errors:
            return {"type": "song.error", "detail": dict(errors)}
        artist_obj = await Artist.objects.get(name=message["artist"])
        await song.update(
            title=message["title"], content=message["content"], artist=artist_obj
        )
        song_dict = await song.get_dict()
        return song_dict

    async def delete_song(self, message: typing.Dict) -> typing.Dict:
        id = int(message.pop("id"))
        try:
            song = await Song.objects.get(id=id)
        except NoMatch:
            return {"type": "song.missing", "detail": "Song not found"}
        await song.delete()
        return {"type": "song.deleted", "detail": "Song successfully deleted"}

    async def transpose_song(self, message: typing.Dict) -> typing.Dict:
        content = message["content"]
        degree = int(message["degree"])
        parser = Parser(content)
        parser.transpose(degree)
        return {
            "type": "song.transposed",
            "content": parser.content,
            "html": parser.html,
        }

    async def create_artist(self, message: typing.Dict) -> typing.Dict:
        name = message["name"]
        await Artist.objects.create(name=name)
        return {"type": "artist.created", "name": name}

    # async def on_chord_hover(self, websocket, message) -> str:
    #     # TODO: Maybe not do it this way?
    #     chord = message["chord"]
    #     variation = message["variation"]
    #     # TODO: Generate all the static files
    #     img_src = "http://127.0.0.1/static/{chord}/{variation}.png"
    #     response = json.dumps({"type": "chord.hover", "img_src": img_src})
    #     return response


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

import typing

from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from .schema import SongSchema
from .models import database, Song
from .parser import Parser


app = Starlette()
app.debug = True


@app.route("/songs")
class SongEndpoint(HTTPEndpoint):
    async def get(self, request) -> JSONResponse:
        songs = await Song.objects.all()
        return JSONResponse([{"title": song.title, "id": song.id} for song in songs])


@app.websocket_route("/ws")
class ComposerWebSocket(WebSocketEndpoint):

    encoding = "json"

    async def on_receive(self, websocket, message: typing.Dict) -> None:
        method = f"{message.pop('type').split('.')[1]}"
        response = await getattr(self, method)(message)
        await websocket.send_json(response)

    async def create(self, message: typing.Dict) -> typing.Dict:
        _, errors = SongSchema.validate_or_error(message)
        song_obj = await Song.objects.create(**message)
        song_dict = song_obj.get_dict(new=True)
        return song_dict

    async def detail(self, message: typing.Dict) -> typing.Dict:
        song = await Song.objects.get(id=message["id"])
        if not song:
            return {"type": "song.missing", "detail": "Song not found"}
        song_dict = song.get_dict()
        return song_dict

    async def update(self, message: typing.Dict) -> typing.Dict:
        id = message.pop("id")
        song_obj = await Song.objects.get(id=id)
        if not song_obj:
            return {"type": "song.missing", "detail": "Song not found"}
        _, errors = SongSchema.validate_or_error(message)
        if errors:
            return {"type": "song.error", "detail": dict(errors)}
        await song_obj.update(**message)
        song_dict = song_obj.get_dict()
        return song_dict

    async def delete(self, message: typing.Dict) -> typing.Dict:
        id = message.pop("id")
        song_obj = await Song.objects.get(id=id)
        if not song_obj:
            return {"type": "song.missing", "detail": "Song not found"}
        await song_obj.delete()
        return {"type": "song.deleted", "detail": "Song successfully deleted"}

    async def transpose(self, message: typing.Dict) -> typing.Dict:
        content = message["content"]
        degree = int(message["degree"])
        parser = Parser(content)
        parser.transpose(degree)
        return {
            "type": "song.transposed",
            "content": parser.content,
            "html": parser.html,
        }

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

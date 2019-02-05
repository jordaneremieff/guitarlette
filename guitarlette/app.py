import json

from tortoise import Tortoise
from tortoise.transactions import in_transaction

from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import TemplateResponse
from starlette.config import Config

from guitarlette.parser import Parser
from guitarlette.models import Song, Revision

# config = Config(".env")

# DEBUG = config("DEBUG", cast=bool, default=False)
# DATABASE_URL = config("DATABASE_URL", cast=str)
# WEBSOCKET_URL = config("WEBSOCKET_URL", cast=str)
# TEMPLATE_DIR = config("TEMPLATE_DIR", cast=str)
# STATIC_DIR = config("STATIC_DIR", cast=str)

DEBUG = True
DATABASE_URL = "sqlite://guitarlette.db"
WEBSOCKET_URL = "ws://127.0.0.1:8000/ws"
TEMPLATE_DIR = "templates"
STATIC_DIR = "static"


app = Starlette(debug=DEBUG, template_directory=TEMPLATE_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
async def on_startup() -> None:
    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["guitarlette.models"]})


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await Tortoise.close_connections()


@app.route("/", name="list")
@app.route("/new", name="new")
@app.route("/{id:int}", name="detail")
class Composer(HTTPEndpoint):
    async def get(self, request) -> TemplateResponse:
        template = "composer.html"
        context = {"request": request, "WEBSOCKET_URL": WEBSOCKET_URL}
        if "id" in request.path_params:
            song = await Song.get(id=request.path_params["id"])
            context["song"] = song
        elif request.url.path == "/":
            context["songs"] = await Song.all()
            template = "list.html"
        return TemplateResponse(app.get_template(template), context)


@app.websocket_route("/ws")
class ComposerWebSocket(WebSocketEndpoint):

    encoding = "json"

    async def on_receive(self, websocket, message) -> None:
        handler_name = message["type"].split(".")[1]
        handler = getattr(self, handler_name, None)
        response = await handler(websocket, message)
        await websocket.send_json(response)

    async def create(self, websocket, message):
        song = await Song.create(
            title=message["title"], content=message["content"], artist=message["artist"]
        )
        return {"id": song.id}

    async def update(self, websocket, message) -> str:
        async with in_transaction():
            song = await Song.get(id=int(message["id"]))
            await Revision.create(title=song.title, content=song.content, song=song)
            if "title" in message:
                song.title = message["title"]
            if "content" in message:
                song.content = message["content"]
            if "artist" in message:
                song.artist = message["artist"]
            await song.save()
        return song.parser.dict

    async def delete(self, websocket, message) -> str:
        song_id = int(message["id"])
        song = await Song.get(id=song_id)
        await song.delete()
        return json.dumps({"type": "song.redirect", "redirect_url": "/"})

    async def transpose(self, websocket, message) -> str:
        content = message["content"]
        degree = int(message["degree"])
        song_parser = Parser(content=content)
        song_parser.transpose(degree)
        return song_parser.dict

    # async def on_chord_hover(self, websocket, message) -> str:
    #     # TODO: Maybe not do it this way?
    #     chord = message["chord"]
    #     variation = message["variation"]
    #     # TODO: Generate all the static files
    #     img_src = "http://127.0.0.1/static/{chord}/{variation}.png"
    #     response = json.dumps({"type": "chord.hover", "img_src": img_src})
    #     return response

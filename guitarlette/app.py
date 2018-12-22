import json

from tortoise import Tortoise
from tortoise.transactions import in_transaction

from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import TemplateResponse
from starlette.config import Config

from guitarlette.parser import SongParser
from guitarlette.models import Song, Revision  # , Notebook

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
DATABASE_URL = config("DATABASE_URL", cast=str)
WEBSOCKET_URL = config("WEBSOCKET_URL", cast=str)
TEMPLATE_DIR = config("TEMPLATE_DIR", cast=str)
STATIC_DIR = config("STATIC_DIR", cast=str)

app = Starlette(debug=DEBUG, template_directory=TEMPLATE_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
async def on_startup() -> None:
    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["guitarlette.models"]})


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await Tortoise.close_connections()


@app.route("/", name="dashboard")
class Dashboard(HTTPEndpoint):
    async def get(self, request) -> TemplateResponse:
        # songs = await Song.all()
        context = {"request": request}
        return TemplateResponse(app.get_template("dashboard.html"), context)


@app.route("/songs", name="song-list")
class SongList(HTTPEndpoint):
    async def get(self, request) -> TemplateResponse:
        songs = await Song.all()
        context = {"request": request, "songs": songs}
        return TemplateResponse(app.get_template("list.html"), context)


@app.route("/songs/compose", name="song-composer")
@app.route("/songs/compose/{song_id:int}", name="song-detail")
class SongComposer(HTTPEndpoint):
    async def get(self, request) -> TemplateResponse:
        context = {"request": request, "WEBSOCKET_URL": WEBSOCKET_URL}
        if "song_id" in request.path_params:
            song = await Song.get(id=request.path_params["song_id"])
            context["song"] = song
        return TemplateResponse(app.get_template("composer.html"), context)


@app.websocket_route("/ws")
class SongComposerWebSocket(WebSocketEndpoint):

    encoding = "json"

    async def on_receive(self, websocket, message) -> None:
        method = f"on_{message.pop('type').replace('.', '_')}"
        response = await getattr(self, method)(websocket, message)
        await websocket.send_text(response)

    async def on_song_create(self, websocket, message) -> str:
        title = message["title"]
        content = message["content"]
        song = await Song.create(title=title, content=content)
        redirect_url = app.url_path_for("song-detail", song_id=song.id)
        return json.dumps({"type": "song.redirect", "redirect_url": redirect_url})

    async def on_song_update(self, websocket, message) -> str:
        song_id = int(message["id"])

        async with in_transaction():
            song = await Song.get(id=song_id)
            await Revision.create(title=song.title, content=song.content, song=song)

            if "title" in message:
                song.title = message["title"]
            if "content" in message:
                song.content = message["content"]
            # if "artist" in message:
            #     song.artist = message["artist"]

            await song.save()

        return song.json

    async def on_song_delete(self, websocket, message) -> str:
        song_id = int(message["id"])
        song = await Song.get(id=song_id)
        await song.delete()
        redirect_url = app.url_path_for("dashboard")
        return json.dumps({"type": "song.redirect", "redirect_url": redirect_url})

    async def on_song_transpose(self, websocket, message) -> str:
        content = message["content"]
        degree = int(message["degree"])
        song_parser = SongParser(content=content)
        song_parser.transpose(degree)
        return song_parser.json

    async def on_chord_hover(self, websocket, message) -> str:
        # TODO: Maybe not do it this way?
        chord = message["chord"]
        variation = message["variation"]
        # TODO: Generate all the static files
        img_src = "http://127.0.0.1/static/{chord}/{variation}.png"
        response = json.dumps({"type": "chord.hover", "img_src": img_src})
        return response


# @app.route("/notebooks", name="notebook-list")
# @app.route("/notebooks/create", name="notebook-create")
# @app.route("/notebooks/update/{notebook_id:int}", name="notebook-retrieve")
# @app.route("/notebooks/delete/{notebook_id:int}", name="notebook-delete")
# class Notebooks(HTTPEndpoint):
#     async def get(self, request) -> TemplateResponse:
#         notebooks = await Notebook.all().prefetch_related("songs")
#         context = {"request": request, "notebooks": notebooks}
#         return TemplateResponse(app.get_template("notebooks.html"), context)

#     async def create(self, request) -> TemplateResponse:
#         pass

#     async def update(self, request) -> TemplateResponse:
#         pass

#     async def delete(self, request) -> TemplateResponse:
#         pass

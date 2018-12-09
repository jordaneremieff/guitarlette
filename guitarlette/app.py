import json

from tortoise import Tortoise
from graphql.execution.executors.asyncio import AsyncioExecutor

from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint

# from starlette.datastructures import DatabaseURL
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.graphql import GraphQLApp
from starlette.config import Config

from guitarlette.schema import schema
from guitarlette.parser import SongParser
from guitarlette.models import Song
from guitarlette.schema.queries import CREATE_SONG_MUTATION, UPDATE_SONG_MUTATION


config = Config(".env")


DEBUG = config("DEBUG", cast=bool, default=False)
DATABASE_URL = config("DATABASE_URL", cast=str)
WEBSOCKET_URL = config("WEBSOCKET_URL", cast=str)


app = Starlette(debug=DEBUG, template_directory="templates/")
app.mount("/static", StaticFiles(directory="static/"), name="static")
graphql_app = GraphQLApp(schema=schema, executor=AsyncioExecutor())
app.add_route("/graphql", graphql_app)


@app.on_event("startup")
async def on_startup() -> None:
    """Create the database connection."""
    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["guitarlette.models"]})


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Cleanup the database connection."""
    await Tortoise.close_connections()


def render_response(request, template: str, context: dict) -> HTMLResponse:
    req_ctx = {"request": request}
    resp_ctx = {**req_ctx, **context}
    content = app.get_template(template).render(**resp_ctx)
    return HTMLResponse(content)


@app.route("/")
class Homepage(HTTPEndpoint):
    async def get(self, request):
        songs = await Song.all()
        context = {"songs": songs}
        return render_response(request, "index.html", context)


@app.route("/compose")
@app.route("/compose/{song_id:int}")
class Composer(HTTPEndpoint):
    async def get(self, request):
        context = {"WEBSOCKET_URL": WEBSOCKET_URL}
        if "song_id" in request.path_params:
            song_id = request.path_params["song_id"]
            song = await Song.get(id=song_id)
            song_parser = SongParser(content=song.content)
            context["song"] = song
            context["song_parser"] = song_parser
        return render_response(request, "compose.html", context)


@app.websocket_route("/ws")
class GraphQLWebSocket(WebSocketEndpoint):

    encoding = "text"

    async def on_receive(self, websocket, message) -> None:
        message = json.loads(message)
        method = f"on_{message.pop('type').replace('.', '_')}"
        response = await getattr(self, method)(websocket, message)
        await websocket.send_text(response)

    async def on_song_create(self, websocket, message) -> str:
        res = await graphql_app.execute(
            websocket, query=CREATE_SONG_MUTATION, variables=message
        )
        content = res.data["createSong"]["song"]["content"]
        song_parser = SongParser(content=content)
        return song_parser.json

    async def on_song_update(self, websocket, message) -> str:
        res = await graphql_app.execute(
            websocket, query=UPDATE_SONG_MUTATION, variables=message
        )
        content = res.data["updateSong"]["song"]["content"]
        song_parser = SongParser(content=content)
        return song_parser.json

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

import json

from tortoise import Tortoise
from graphql.execution.executors.asyncio import AsyncioExecutor

from starlette.endpoints import WebSocketEndpoint
from starlette.datastructures import DatabaseURL
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.graphql import GraphQLApp
from starlette.config import Config

from guitarlette.endpoints import TemplateEndpoint
from guitarlette.schema import schema
from guitarlette.parser import SongParser
from guitarlette.models import Song
from guitarlette.schema.queries import CREATE_SONG_MUTATION, UPDATE_SONG_MUTATION


config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
DATABASE_URL = config("DATABASE_URL", cast=DatabaseURL)
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


@app.route("/")
class Homepage(TemplateEndpoint):

    template_name = "index.html"

    async def get_context(self, request) -> dict:
        context = await super().get_context(request)
        songs = await Song.all()
        context["songs"] = songs
        return context


@app.route("/compose")
@app.route("/compose/{song_id:int}")
class Composer(TemplateEndpoint):

    template_name = "compose.html"

    async def get_context(self, request) -> dict:
        context = await super().get_context(request)
        if "song_id" in request.path_params:
            song = await Song.get(id=request.path_params["song_id"])
            song_parser = SongParser(content=song.content)
            context = {"song": song, "song_parser": song_parser}
        context["WEBSOCKET_URL"] = WEBSOCKET_URL
        return context


@app.websocket_route("/ws")
class GraphQLWebSocket(WebSocketEndpoint):

    encoding = "text"

    async def on_receive(self, websocket, message) -> None:
        message = json.loads(message)
        method = f"on_{message.pop('type').replace('.', '_')}"
        song_parser = await getattr(self, method)(message)
        response = {"content": song_parser.content, "html": song_parser.html}
        await websocket.send_text(json.dumps(response))

    async def on_song_create(self, message) -> SongParser:
        res = await self.scope["app"].graphql_app.execute(
            query=CREATE_SONG_MUTATION, variables=message
        )
        content = res.data["createSong"]["song"]["content"]
        return SongParser(content=content)

    async def on_song_update(self, message) -> SongParser:
        res = await self.scope["app"].graphql_app.execute(
            query=UPDATE_SONG_MUTATION, variables=message
        )
        content = res.data["updateSong"]["song"]["content"]
        return SongParser(content=content)

    async def on_song_transpose(self, message) -> SongParser:
        content = message["content"]
        degree = int(message["degree"])
        song_parser = SongParser(content=content)
        song_parser.transpose(degree)
        return song_parser

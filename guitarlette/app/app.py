import json

from starlette.endpoints import WebSocketEndpoint

from guitarlette.endpoints import TemplateEndpoint
from guitarlette.models import Song
from guitarlette.parser import SongParser
from guitarlette.application import Guitarlette
from guitarlette.app.settings import Config
from guitarlette.schema.queries import CREATE_SONG_MUTATION, UPDATE_SONG_MUTATION


app = Guitarlette(config=Config())


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
            context["song_id"] = song.id
            context["song_name"] = song.name
            context["song_content"] = song.content
            context["song_parser"] = song_parser
        context["WEBSOCKET_URL"] = app.config.WEBSOCKET_URL
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

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
            song_parser = SongParser(raw_data=song.content)
            context["song_id"] = song.id
            context["song_name"] = song.name
            context["song_content"] = song.content
            context["song_parser"] = song_parser
        context["WEBSOCKET_URL"] = app.config.WEBSOCKET_URL
        return context


@app.websocket_route("/ws")
class GraphQLWebSocket(WebSocketEndpoint):

    encoding = "text"

    async def on_receive(self, websocket, message):
        message = json.loads(message)
        message_type = message.pop("type")
        if message_type == "song.transpose":
            content = message["content"]
            degree = int(message["degree"])
            song_parser = SongParser(raw_data=content)
            song_parser.transpose(degree)
        else:
            mutation_type = message_type.split(".")[1]

            if message_type == "song.create":
                mutation = CREATE_SONG_MUTATION

            elif message_type == "song.update":
                mutation = UPDATE_SONG_MUTATION

            res = await self.scope["app"].graphql_app.execute(
                query=mutation, variables=message
            )
            content = res.data[f"{mutation_type}Song"]["song"]["content"]

            song_parser = SongParser(raw_data=content)

        await websocket.send_text(
            json.dumps({"raw_data": song_parser.raw_data, "content": song_parser.html})
        )

import json

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.graphql import GraphQLApp
from starlette.endpoints import WebSocketEndpoint

from tortoise import Tortoise
from graphql.execution.executors.asyncio import AsyncioExecutor

from guitarlette.schema import schema
from guitarlette.endpoints import TemplateEndpoint
from guitarlette.models import Song
from guitarlette.parser import SongParser
from guitarlette.config import Config

from guitarlette.local_settings import DEBUG, TEMPLATE_DIR, STATIC_DIR, DATABASE


class Guitarlette(Starlette):
    """
    Implements various project-specific defaults and configuration by overriding the
    base `Starlette` application to organize the general behaviour and tweak the
    interface to my preferences.

    All of this functionality (except the `config` parameter and convenience methods)
    can be achieved using decorator patterns.
    """

    def __init__(self, config: Config) -> None:
        super().__init__(debug=config.DEBUG, template_directory=config.TEMPLATE_DIR)
        self.config = config
        self.graphql_app = GraphQLApp(schema=schema, executor=AsyncioExecutor())
        # Add exception handlers
        self.add_exception_handler(500, self.server_error)
        self.add_exception_handler(404, self.not_found)
        # Mount static files
        self.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
        # Add GraphQL route
        self.add_route("/graphql", self.graphql_app)
        # Add startup/shutdown event handlers
        self.lifespan_handler.add_event_handler("startup", self.on_startup)
        self.lifespan_handler.add_event_handler("shutdown", self.on_shutdown)

    def get_exception_response(self, request, code: int) -> HTMLResponse:
        """
        Retrieve and render the template for a specified exception response.
        """
        template = self.get_template(f"{code}.html")
        content = template.render(request=request)
        return HTMLResponse(content, status_code=code)

    async def on_startup(self) -> None:
        """
        Startup event handler. Initialize the database connection.
        """
        await Tortoise.init(**self.config.DATABASE)

    async def on_shutdown(self) -> None:
        """
        Shutdown event handler. Close the database connections.
        """
        await Tortoise.close_connections()

    async def server_error(self, request, exc) -> HTMLResponse:
        """
        Handle internal server error (500) responses.
        """
        return self.get_exception_response(request, 500)

    async def not_found(self, request, exc) -> HTMLResponse:
        """
        Handle not found (404) responses.
        """
        return self.get_exception_response(request, 404)


config = Config(
    DEBUG=DEBUG, TEMPLATE_DIR=TEMPLATE_DIR, STATIC_DIR=STATIC_DIR, DATABASE=DATABASE
)

app = Guitarlette(config=config)


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
            context["song_html"] = song_parser.html
        context["WEBSOCKET_URL"] = "ws://127.0.0.1:8000/ws"
        return context


@app.websocket_route("/ws")
class GraphQLWebSocket(WebSocketEndpoint):

    encoding = "text"

    async def on_receive(self, websocket, request_data):
        variables = json.loads(request_data)
        mutation = """
            mutation createSong($name: String!, $content: String!) {
              createSong(name: $name, content: $content) {
                song {
                  id
                  name
                  content
                }
              }
            }
        """
        res = await self.scope["app"].graphql_app.execute(
            query=mutation, variables=variables
        )
        content = res.data["createSong"]["song"]["content"]
        song_parser = SongParser(raw_data=content)

        await websocket.send_text(json.dumps({"content": song_parser.html}))

import uvicorn
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
from guitarlette.config import Config

from guitarlette.parser import song_parser


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
class Composer(TemplateEndpoint):

    template_name = "compose.html"

    async def get_context(self, request) -> dict:
        context = await super().get_context(request)
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
        parsed = song_parser(content)
        html = parsed.html

        await websocket.send_text(json.dumps({"content": html}))

        # TODO: Parse the mutation result and assign chord values where they can be
        # detected, then return that in the WS response.
        # Once the chords are parsed we can then do all sorts of things.


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, debug=True)

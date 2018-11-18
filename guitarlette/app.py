import uvicorn
from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.graphql import GraphQLApp
from tortoise import Tortoise

from guitarlette.schema import schema
from guitarlette.endpoints import TemplateEndpoint
from guitarlette.models import Song
from guitarlette.config import DB_CONFIG


class Guitarlette(Starlette):
    """
    Implements various project-specific defaults and configuration by overriding the
    base `Starlette` application to organize the general behaviour and tweak the
    interface to my preferences.

    All of this functionality (except the `config` parameter and convenience methods)
    can be achieved using decorator patterns.
    """

    def __init__(self, config: dict) -> None:
        debug = config.get("debug", False)
        template_directory = config["TEMPLATE_DIR"]
        super().__init__(debug=debug, template_directory=template_directory)
        self.config = config
        # Add exception handlers
        self.add_exception_handler(500, self.server_error)
        self.add_exception_handler(404, self.not_found)
        # Mount static files
        self.mount(
            "/static", StaticFiles(directory=config["STATIC_DIR"]), name="static"
        )
        # Add GraphQL route
        self.add_route(
            "/graphql", GraphQLApp(schema=schema, executor=AsyncioExecutor())
        )
        # Add startup/shutdown event handlers
        self.lifespan_handler.add_event_handler("startup", self.on_startup)
        self.lifespan_handler.add_event_handler("shutdown", self.on_shutdown)

    def get_exception_response(self, request, code: int) -> HTMLResponse:
        """Retrieve and render the template for a specified exception response."""
        template = self.get_template(f"{code}.html")
        content = template.render(request=request)
        return HTMLResponse(content, status_code=code)

    async def on_startup(self) -> None:
        """Startup event handler. Initialize the database connection."""
        await Tortoise.init(**DB_CONFIG)

    async def on_shutdown(self) -> None:
        """Shutdown event handler. Close the database connections."""
        await Tortoise.close_connections()

    async def server_error(self, request, exc) -> HTMLResponse:
        """Handle internal server error (500) responses."""
        return self.get_exception_response(request, 500)

    async def not_found(self, request, exc) -> HTMLResponse:
        """Handle not found (404) responses."""
        return self.get_exception_response(request, 404)


app = Guitarlette(
    config={"DEBUG": True, "TEMPLATE_DIR": "templates", "STATIC_DIR": "static"}
)


@app.route("/")
class Homepage(TemplateEndpoint):

    template_name = "index.html"

    async def get_context(self, request) -> dict:
        context = await super().get_context(request)
        songs = await Song.all()
        context["songs"] = songs
        return context


# @app.route("/songs/new", name="create-song")
# class CreateSong(TemplateEndpoint):

#     template_name = "compose.html"


# @app.route("/songs/update/{id}")
# class UpdateSong(TemplateEndpoint):

#     template_name = "compose.html"

#     async def get_context(self, request):
#         context = await super().get_context(request)
#         context["song_list"] = await SongQuery(app.get_db()).get(
#             id=self.scope["app"].path_params["id"]
#         )
#         return context


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, debug=True)

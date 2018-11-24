from tortoise import Tortoise
from graphql.execution.executors.asyncio import AsyncioExecutor

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.graphql import GraphQLApp

from guitarlette.schema import schema


class Guitarlette(Starlette):
    def __init__(self, config) -> None:
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
        """Render the response for an exception handler."""
        template = self.get_template(f"{code}.html")
        content = template.render(request=request)
        return HTMLResponse(content, status_code=code)

    async def on_startup(self) -> None:
        """Create the database connection."""
        await Tortoise.init(**self.config.DATABASE)

    async def on_shutdown(self) -> None:
        """Cleanup the database connections."""
        await Tortoise.close_connections()

    async def server_error(self, request, exc) -> HTMLResponse:
        """Handle internal server error (500) responses."""
        return self.get_exception_response(request, 500)

    async def not_found(self, request, exc) -> HTMLResponse:
        """Handle not found (404) responses."""
        return self.get_exception_response(request, 404)

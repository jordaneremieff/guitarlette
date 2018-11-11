import uvicorn

from graphql.execution.executors.asyncio import AsyncioExecutor

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.graphql import GraphQLApp

from guitarlette.schema import schema
from guitarlette.endpoints import TemplateEndpoint
from guitarlette.database.connection import Connection
from guitarlette.database.models import SongQuery

db = Connection(database="guitarlette")

app = Starlette(debug=True, template_directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_route("/graphql", GraphQLApp(schema=schema, executor=AsyncioExecutor()))


@app.on_event("startup")
async def open_database_connection_pool():
    await db.create_connection()
    app.db = db


@app.on_event("shutdown")
async def close_database_connection_pool():
    await app.db.close_connection()


@app.exception_handler(404)
async def not_found(request, exc):
    template = app.get_template("404.html")
    content = template.render(request=request)
    return HTMLResponse(content, status_code=404)


@app.exception_handler(500)
async def server_error(request, exc):
    template = app.get_template("500.html")
    content = template.render(request=request)
    return HTMLResponse(content, status_code=500)


@app.route("/")
class Homepage(TemplateEndpoint):

    template_name = "index.html"

    async def get_context(self, request):
        context = await super().get_context(request)
        context["song_list"] = await SongQuery(app.db).list()
        return context


@app.route("/songs/new")
class CreateSong(TemplateEndpoint):

    template_name = "compose.html"


@app.route("/songs/update/{id}")
class UpdateSong(TemplateEndpoint):

    template_name = "compose.html"

    async def get_context(self, request):
        context = await super().get_context(request)
        context["song_list"] = await SongQuery(app.db).get(
            id=self.scope["app"].path_params["id"]
        )
        return context


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

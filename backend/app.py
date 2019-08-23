# from .parser import Parser
# from .models import Song, Revision

from starlette.endpoints import HTTPEndpoint
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from databases import Database

database = Database("sqlite:///guitarlette.db")


app = Starlette()
app.debug = True


@app.route("/songs", name="list")
@app.route("/songs/{id:int}", name="detail")
class Composer(HTTPEndpoint):
    async def get(self, request) -> JSONResponse:
        song_id = request.path_params.get("id")
        if song_id:
            query = "SELECT * FROM songs WHERE id = :id"
            result = await database.fetch_one(query=query, values={"id": song_id})
            return JSONResponse(dict(result))
        query = "SELECT * FROM songs"
        result = await database.fetch_all(query=query)
        data = [dict(row) for row in result]
        return JSONResponse(data)

    async def post(self, request) -> JSONResponse:
        song_id = request.path_params.get("id")
        form = await request.form()
        values = dict(form)
        if song_id:
            query = "UPDATE songs SET title = :title, artist = :artist, content = :content WHERE id = :id"
            values["id"] = song_id
        else:
            query = "INSERT INTO songs(title, artist, content) VALUES (:title, :artist, :content)"
        await database.execute(query=query, values=values)
        return JSONResponse(dict(values))


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.add_middleware(CORSMiddleware, allow_origins=["*"])

from starlette.endpoints import HTTPEndpoint
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from databases import Database

from .schema import Song
from .parser import Parser

database = Database("sqlite:///guitarlette.db")


app = Starlette()
app.debug = True


@app.route("/songs")
@app.route("/songs/{id:int}")
class SongEndpoint(HTTPEndpoint):
    async def get(self, request) -> JSONResponse:
        song_id = request.path_params.get("id")
        if song_id:
            query = """
            SELECT * FROM songs WHERE id = :id
            """
            result = await database.fetch_one(query=query, values={"id": song_id})
            if not result:
                return JSONResponse({"detail": "Not found"}, status_code=404)
            song = dict(result)
            song["viewer_content"] = Parser(song["content"]).html
            return JSONResponse(song)
        else:
            query = "SELECT * FROM songs"

        result = await database.fetch_all(query=query)
        data = [dict(row) for row in result]
        return JSONResponse(data)

    async def post(self, request) -> JSONResponse:
        form = await request.form()
        data = dict(form)
        song, errors = Song.validate_or_error(data)
        if errors:
            return JSONResponse(dict(errors), status_code=400)

        song_id = request.path_params.get("id")
        song = dict(song)

        if song_id:
            query = """
            UPDATE songs
            SET title = :title, artist = :artist, content = :content
            WHERE id = :id
            """
        else:
            query = """
            INSERT INTO songs(title, artist, content)
            VALUES (:title, :artist, :content)
            """

        result = await database.execute(query=query, values=song)

        if not song_id:
            song["id"] = result
            song["redirect"] = True

        song["viewer_content"] = Parser(song["content"]).html

        return JSONResponse(song)


@app.route("/transpose")
class ComposerEndpoint(HTTPEndpoint):
    async def post(self, request) -> JSONResponse:
        form = await request.form()
        data = dict(form)
        content = data["content"]
        degree = int(data["degree"])
        parsed = Parser(content)
        parsed.transpose(degree)
        response = {"content": parsed.content, "viewer_content": parsed.html}
        return JSONResponse(response)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.add_middleware(CORSMiddleware, allow_origins=["*"])

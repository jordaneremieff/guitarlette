from starlette.endpoints import HTTPEndpoint
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from .schema import SongSchema
from .models import database, Song
from .parser import Parser


app = Starlette()
app.debug = True


@app.route("/songs")
@app.route("/songs/{id:int}")
class SongEndpoint(HTTPEndpoint):
    async def get(self, request) -> JSONResponse:
        song_id = request.path_params.get("id")
        if song_id:
            song = await Song.objects.get(id=song_id)
            if not song:
                return JSONResponse({"detail": "Not found"}, status_code=404)
            song_dict = song.get_dict()
            return JSONResponse(song_dict)
        else:
            songs = await Song.objects.all()
            return JSONResponse([song.get_dict() for song in songs])

    async def post(self, request) -> JSONResponse:
        form = await request.form()
        data = dict(form)
        validated_data, errors = SongSchema.validate_or_error(data)
        if errors:
            return JSONResponse(dict(errors), status_code=400)
        validated_data = dict(validated_data)
        song_id = request.path_params.get("id")
        if song_id:
            song = await Song.objects.get(id=song_id)
            await song.update(**validated_data)
            song_dict = song.get_dict()
        else:
            song = await Song.objects.create(**validated_data)
            song_dict = song.get_dict(created=True)
        return JSONResponse(song_dict)

    async def delete(self, request) -> JSONResponse:
        song_id = request.path_params.get("id")
        song = await Song.objects.get(id=song_id)
        await song.delete()
        return JSONResponse({"detail": "Successfully deleted"})


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


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

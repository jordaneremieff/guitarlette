from io import BytesIO
from datetime import datetime
from pathlib import Path

from mangum import Mangum
from fastapi import FastAPI, Request, Body, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .parser import SongParser


templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

app = FastAPI()
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)


@app.get("/")
def compose(request: Request):
    return templates.TemplateResponse("compose.html", {"request": request})


@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.post("/parse")
def parse(content: str = Body(..., embed=True)):
    parser = SongParser(content)
    return {"html_content": parser.html}


@app.post("/transpose")
def transpose(content: str = Body(...), degree: int = Body(...)):
    parser = SongParser(content)
    parser.transpose(degree)
    return {"content": parser.content, "html_content": parser.html}


@app.post("/download")
def download(request: Request, download_content: str = Form(...)):
    filename = f"guitarlette-{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.txt"
    return StreamingResponse(
        BytesIO(download_content.encode()),
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        media_type="text/plain",
    )


handler = Mangum(app, lifespan="off")

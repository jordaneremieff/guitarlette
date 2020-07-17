from pathlib import Path
from io import BytesIO
from datetime import datetime

from mangum import Mangum
from fastapi import FastAPI, Request, Body, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .song import Song


BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = str(BASE_DIR / "templates")
STATIC_DIR = str(BASE_DIR / "static")


templates = Jinja2Templates(directory=TEMPLATE_DIR)
static = StaticFiles(directory=STATIC_DIR)

app = FastAPI()
app.mount("/static", static, name="static")


@app.get("/")
def compose(request: Request):
    return templates.TemplateResponse("compose.html", {"request": request})


@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.post("/parse")
def parse(content: str = Body(..., embed=True)):
    parser = Song(content)
    return {"html_content": parser.html}


@app.post("/transpose")
def transpose(content: str = Body(...), degree: int = Body(...)):
    parser = Song(content, degree=degree)
    return {"content": parser.text, "html_content": parser.html}


@app.post("/download")
def download(request: Request, content: str = Form(...)) -> StreamingResponse:
    filename = f"guitarlette-{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.txt"
    return StreamingResponse(
        BytesIO(content.encode()),
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        media_type="text/plain",
    )


handler = Mangum(app, lifespan="off")


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, debug=True)

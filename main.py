from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import zipfile
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="scormplayer/static"), name="static")
templates = Jinja2Templates(directory="scormplayer/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_scorm(request: Request, file: UploadFile = File(...)):
    file_location = f"scormplayer/static/courses/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    with zipfile.ZipFile(file_location, 'r') as zip_ref:
        zip_ref.extractall("scormplayer/static/courses/")

    os.remove(file_location)

    scorm_url = f"/static/courses/{file.filename.replace('.zip', '')}/index.html"
    return templates.TemplateResponse("player.html", {"request": request, "scorm_url": scorm_url})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

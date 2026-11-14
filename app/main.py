from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.services.thumbnail_analyzer import analyze_thumbnail_bytes, MAX_BYTES

app=FastAPI(title='YouTube Thumbnail Research Analyzer',version='2.0')
STATIC_DIR=Path(__file__).parent/'static'
app.mount('/static',StaticFiles(directory=str(STATIC_DIR)),name='static')

@app.get('/')
def home():
    return FileResponse(str(STATIC_DIR/'index.html'))

@app.get('/health')
def health():
    return {'status':'ok'}

@app.post('/analyze-thumbnail')
async def analyze(file: UploadFile=File(...)):
    if file.content_type not in ('image/jpeg','image/png','image/webp'):
        raise HTTPException(400,'Upload a JPG, PNG or WebP image.')
    content=await file.read(MAX_BYTES+1)
    try:
        return analyze_thumbnail_bytes(content,file.filename or 'thumbnail')
    except ValueError as exc:
        raise HTTPException(400,str(exc)) from exc

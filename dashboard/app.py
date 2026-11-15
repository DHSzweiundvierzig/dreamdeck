"""DreamDeck-Backend: FastAPI-Gerüst."""
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from .config import COMFY_URL

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dieser Client wird ab 2d für alle ComfyUI-Aufrufe genutzt.
    app.state.comfy = httpx.AsyncClient(base_url=COMFY_URL, timeout=2.0)
    try:
        yield
    finally:
        await app.state.comfy.aclose()


app = FastAPI(title="DreamDeck", lifespan=lifespan)


@app.get("/api/health")
async def health(request: Request):
    """Meldet, ob ComfyUI erreichbar ist (wirft nie einen Fehler)."""
    try:
        response = await request.app.state.comfy.get("/system_stats")
        comfy_ok = response.status_code == 200
    except httpx.HTTPError:
        comfy_ok = False
    return {"status": "ok", "comfyui": comfy_ok}


# Statische Dateien zuletzt einhängen, damit die API-Routen Vorrang haben.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

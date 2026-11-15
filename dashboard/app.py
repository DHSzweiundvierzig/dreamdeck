"""DreamDeck-Backend: FastAPI-Gerüst."""
import secrets
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import COMFY_URL
from .workflow import build_flux_workflow

STATIC_DIR = Path(__file__).resolve().parent / "static"


class LoraIn(BaseModel):
    """Eine LoRA mit Dateiname und Stärke."""

    name: str = Field(min_length=1, max_length=200)
    strength: float = Field(default=0.8, ge=-2.0, le=2.0)


class GenerateIn(BaseModel):
    """Bildauftrag für POST /api/generate."""

    prompt: str = Field(min_length=1, max_length=2000)
    # Fehlt der Seed, wird er im Endpunkt zufällig gewählt (0 bis 2^32 - 1).
    seed: int | None = Field(default=None, ge=0)
    width: int = Field(default=768, ge=256, le=2048, multiple_of=16)
    height: int = Field(default=1344, ge=256, le=2048, multiple_of=16)
    steps: int = Field(default=25, ge=1, le=60)
    guidance: float = Field(default=3.5, ge=1.0, le=10.0)
    batch_size: int = Field(default=1, ge=1, le=4)
    loras: list[LoraIn] = Field(default_factory=list, max_length=6)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dieser Client wird ab 2d für alle ComfyUI-Aufrufe genutzt.
    app.state.comfy = httpx.AsyncClient(base_url=COMFY_URL, timeout=2.0)
    # Wird ab 2e für den Fortschritt per Websocket gebraucht.
    app.state.client_id = uuid.uuid4().hex
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


@app.post("/api/generate")
async def generate(job: GenerateIn, request: Request):
    """Baut aus dem Bildauftrag den FLUX-Workflow und schickt ihn an ComfyUI."""
    seed = job.seed if job.seed is not None else secrets.randbelow(2**32)
    workflow, filename_prefix = build_flux_workflow(
        prompt=job.prompt,
        seed=seed,
        width=job.width,
        height=job.height,
        steps=job.steps,
        guidance=job.guidance,
        batch_size=job.batch_size,
        loras=[(lora.name, lora.strength) for lora in job.loras],
    )
    try:
        response = await request.app.state.comfy.post(
            "/prompt",
            json={"prompt": workflow, "client_id": request.app.state.client_id},
            timeout=10.0,
        )
    except httpx.HTTPError:
        return JSONResponse({"fehler": "ComfyUI nicht erreichbar"}, status_code=503)
    # Antwort als JSON lesen; falls ComfyUI etwas anderes schickt, den Rohtext nehmen.
    try:
        answer = response.json()
    except ValueError:
        answer = response.text
    if response.status_code != 200 or not isinstance(answer, dict) or "prompt_id" not in answer:
        return JSONResponse(
            {"fehler": "ComfyUI hat den Auftrag abgelehnt", "details": answer},
            status_code=422,
        )
    return {"prompt_id": answer["prompt_id"], "seed": seed, "filename_prefix": filename_prefix}


# Statische Dateien zuletzt einhängen, damit die API-Routen Vorrang haben.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

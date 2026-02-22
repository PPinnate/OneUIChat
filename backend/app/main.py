from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    ChatRequest,
    DownloadRequest,
    ExploreRequest,
    SettingsPatch,
    SizeRequest,
    StatusResponse,
    TokenRequest,
)
from app.services.download_manager import DownloadManager
from app.services.events import EventBus
from app.services.fit_checker import FitChecker
from app.services.registry import ModelRegistry
from app.services.settings import SettingsStore

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "registry" / "models.json"
CHAT_HISTORY = ROOT / "backend" / "chat_history.jsonl"

app = FastAPI(title="QwenWorkbench Orchestrator", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registry = ModelRegistry(REGISTRY_PATH)
settings = SettingsStore()
events = EventBus()
download_manager = DownloadManager(Path(settings.get()["model_cache_dir"]), events)
fit_checker = FitChecker(registry)


def _refresh_download_cache_path() -> None:
    download_manager.set_cache_dir(Path(settings.get()["model_cache_dir"]))


def _disk_snapshot() -> dict:
    cache_dir = Path(settings.get()["model_cache_dir"]).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(cache_dir)
    return {
        "cache_dir": str(cache_dir),
        "free_bytes": usage.free,
        "free_gb": round(usage.free / (1024**3), 3),
        "total_bytes": usage.total,
        "total_gb": round(usage.total / (1024**3), 3),
    }


@app.get("/models")
def get_models():
    reserve_gb = float(settings.get().get("reserve_gb", registry.machine_profile["default_reserve_gb"]))
    models = []
    for model in registry.all_models():
        variants = []
        for variant in model["variants"]:
            fit = fit_checker.check(model["id"], variant["id"], reserve_gb)
            variants.append({**variant, "fit": fit.model_dump()})
        models.append({**model, "variants": variants})
    return {"machine_profile": registry.machine_profile, "models": models, "disk": _disk_snapshot()}


@app.post("/models/size")
def model_size(payload: SizeRequest):
    try:
        variant = registry.get_variant(payload.model_id, payload.variant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    token = settings.get_token()
    return download_manager.estimate_repo_size(
        variant["repo_id"], token=token, include_file=variant.get("filename") or None
    )


@app.post("/models/explore")
def model_explore(payload: ExploreRequest):
    try:
        variant = registry.get_variant(payload.model_id, payload.variant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    token = payload.token or settings.get_token()
    probe = download_manager.probe_repo(variant["repo_id"], token=token)
    fit = fit_checker.check(payload.model_id, payload.variant_id, float(settings.get().get("reserve_gb", 10)))
    disk = _disk_snapshot()
    enough_disk = disk["free_bytes"] >= probe["total_bytes"] if probe["available"] else False
    return {
        "model_id": payload.model_id,
        "variant_id": payload.variant_id,
        "repo_id": variant["repo_id"],
        "probe": probe,
        "fit": fit.model_dump(),
        "disk": {**disk, "enough_for_download": enough_disk},
        "ready_to_download": bool(probe["available"] and enough_disk),
        "ready_to_load": fit.status == "FITS",
    }


@app.post("/models/download")
async def model_download(payload: DownloadRequest):
    try:
        variant = registry.get_variant(payload.model_id, payload.variant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    token = payload.token or settings.get_token()
    return await download_manager.download_variant(
        repo_id=variant["repo_id"], include_file=variant.get("filename") or None, token=token
    )


@app.get("/settings")
def get_settings():
    return settings.get()


@app.post("/settings")
def patch_settings(payload: SettingsPatch):
    updated = settings.patch(model_cache_dir=payload.model_cache_dir, reserve_gb=payload.reserve_gb)
    _refresh_download_cache_path()
    return updated


@app.post("/settings/token")
def set_token(payload: TokenRequest):
    return settings.save_token(payload.token)


@app.get("/system/status", response_model=StatusResponse)
def status():
    data = settings.get()
    return StatusResponse(
        machine=registry.machine_profile["name"],
        unified_memory_gb=registry.machine_profile["unified_memory_gb"],
        reserve_gb=float(data.get("reserve_gb", 10)),
        workers={},
    )


@app.post("/tasks/chat")
def task_chat(payload: ChatRequest):
    # MVP chat-room UX endpoint; worker-backed inference lands in MVP-2.
    response_text = (
        "QwenWorkbench is ready. Model workers are not loaded yet (MVP-2). "
        "Use Models tab to explore variants, check HF availability, and download explicitly selected variants."
    )
    CHAT_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    CHAT_HISTORY.open("a", encoding="utf-8").write(
        json.dumps(
            {
                "ts": datetime.now(UTC).isoformat(),
                "prompt": payload.prompt,
                "system_prompt": payload.system_prompt,
                "response": response_text,
            }
        )
        + "\n"
    )
    return {"answer": response_text}


@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket):
    await websocket.accept()
    queue = events.subscribe()
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        events.unsubscribe(queue)

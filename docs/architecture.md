# QwenWorkbench Architecture

## Overview
QwenWorkbench is a localhost-only orchestration app that provides one LM Studio–style web UI for multiple local AI tasks.

## Orchestrator responsibilities (implemented now)
1. **ModelRegistry**: static metadata from `registry/models.json`.
2. **DownloadManager**: Hugging Face file listing, size summary, gated-access probing, and per-file download progress.
3. **VariantSelector**: user-chosen variant only.
4. **FitChecker**: validates fit against 48GB unified memory profile with adjustable reserve.
5. **SettingsStore**: cache path, memory reserve, HF token storage (keyring first; config fallback warning).
6. **TaskRouter (MVP stub)**: chat endpoint for ChatGPT-like UI while worker-backed inference lands in MVP-2.

## Startup and install UX
- `QwenWorkbench.command` is a macOS-clickable launcher that creates `.venv`, installs deps, starts backend/frontend, and opens browser.

## API surface (current)
- `GET /models`
- `POST /models/size`
- `POST /models/explore` (availability/auth/size/disk/load-fit)
- `POST /models/download`
- `POST /settings/token`
- `GET /settings`
- `GET /system/status`
- `POST /tasks/chat`
- `WS /ws/events` for download progress/logs

## Process isolation roadmap
Heavy runtimes stay in separate OS processes (`llama-server` / python workers). Reliable unload remains process termination in MVP-1+.

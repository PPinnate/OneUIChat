# QwenWorkbench Agent Guide

## Scope
These instructions apply to the entire repository.

## Mission
Build **QwenWorkbench**: a local-first AI workbench for Apple Silicon M3 Max (48GB unified memory), with explicit user-driven model variant selection and strict process-isolated runtimes.

## Engineering conventions
- Backend: Python 3.11+, FastAPI, typed code, small modules.
- Frontend: React + TypeScript (Vite), minimal dependencies.
- Keep model/runtime logic in backend services (no business logic in route files).
- Use explicit names (`variant_id`, `fits`, `estimated_bytes`) and avoid magic values.
- Never auto-downgrade quantization or silently mutate user settings.

## Safety and product constraints
- Variant selection is always user-driven.
- FitChecker validates and blocks loads that do not fit memory budget.
- If not fit, surface alternatives that fit from installed variants.
- Target machine profile defaults to M3 Max with 48GB unified memory.

## Running locally
- `make dev` starts backend and frontend.
- `make test` runs backend tests and frontend lint.

## Commit style
- Prefer concise, imperative commit subjects.
- Include docs updates whenever architecture changes.

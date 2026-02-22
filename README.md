# QwenWorkbench

Local macOS AI hub for Apple Silicon M3 Max (48GB unified memory), designed as a single orchestrated web app.

## One-click launch on macOS
1. Double-click `QwenWorkbench.command`.
2. It will:
   - create `.venv`
   - install backend + frontend dependencies
   - start backend and frontend
   - auto-open `http://127.0.0.1:5173`

## What happens in Models tab
- Explicit user-selected variants only (no auto quant downgrade).
- **Explore availability + size** checks:
  - if HF token is required
  - total download size from HF
  - disk free-space sufficiency
  - memory fit estimate for loading

## Development
```bash
make setup
make dev
```

## Tests
```bash
make test
```

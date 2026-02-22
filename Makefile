.PHONY: setup dev backend frontend test

setup:
	python3 -m venv .venv
	. .venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -e backend[dev]
	cd frontend && npm install

dev:
	@echo "Starting backend and frontend..."
	@( . .venv/bin/activate && cd backend && python -m uvicorn app.main:app --reload --port 8000 ) & \
	 (cd frontend && npm run dev -- --host 127.0.0.1 --port 5173)

backend:
	. .venv/bin/activate && cd backend && python -m uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev -- --host 127.0.0.1 --port 5173

test:
	. .venv/bin/activate && cd backend && pytest
	cd frontend && npm run lint

.PHONY: install dev backend frontend test lint format docker-up docker-down

install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Run 'make backend' and 'make frontend' in separate terminals"

backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && . .venv/bin/activate && pytest -v
	cd frontend && npm run typecheck

lint:
	cd backend && . .venv/bin/activate && python -m compileall app
	cd frontend && npm run lint

format:
	cd backend && . .venv/bin/activate && python -m compileall app

docker-up:
	docker compose up --build

docker-down:
	docker compose down

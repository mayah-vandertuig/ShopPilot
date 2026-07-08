.PHONY: install install-backend install-frontend dev backend frontend test lint format docker-up docker-down

BACKEND_DIR = backend
VENV_PY = $(BACKEND_DIR)/.venv/bin/python

install: install-backend install-frontend

install-backend:
	cd $(BACKEND_DIR) && \
		python3 -m venv .venv && \
		.venv/bin/python -m ensurepip --upgrade 2>/dev/null || true && \
		.venv/bin/python -m pip install --upgrade pip setuptools wheel && \
		.venv/bin/python -m pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

dev:
	@chmod +x scripts/dev.sh
	@./scripts/dev.sh

backend:
	@test -x $(VENV_PY) || (echo "Run 'make install-backend' first." && exit 1)
	cd $(BACKEND_DIR) && .venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	@test -x $(VENV_PY) || (echo "Run 'make install-backend' first." && exit 1)
	cd $(BACKEND_DIR) && .venv/bin/python -m pytest -v

test-frontend:
	cd frontend && npm run typecheck

lint:
	@test -x $(VENV_PY) || (echo "Run 'make install-backend' first." && exit 1)
	cd $(BACKEND_DIR) && .venv/bin/python -m compileall app
	cd frontend && npm run lint

format:
	@test -x $(VENV_PY) || (echo "Run 'make install-backend' first." && exit 1)
	cd $(BACKEND_DIR) && .venv/bin/python -m compileall app

docker-up:
	docker compose up --build

docker-down:
	docker compose down

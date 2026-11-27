# Run every target from the repo root. Windows users: see the equivalent plain commands in README.md.
PY ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: install dev-backend dev-frontend test build serve snapshot

install:
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r backend/requirements.txt
	cd frontend && npm ci

dev-backend:
	$(BIN)/uvicorn backend.app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	$(BIN)/pytest
	cd frontend && npm run typecheck && npm test

build:
	cd frontend && npm run build

serve: build
	$(BIN)/uvicorn backend.app.main:app --port 8000

# Safe zip of the working tree (incl. uncommitted files) -> snapshots/. Extra flags: make snapshot ARGS="--name foo"
snapshot:
	$(PY) scripts/snapshot.py $(ARGS)

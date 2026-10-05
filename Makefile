SHELL := /bin/zsh

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BACKEND := $(ROOT)/backend
FRONTEND := $(ROOT)/frontend

.PHONY: help install \
	dev-api dev-ui \
	backend-test frontend-test test \
	backend-lint frontend-lint lint \
	backend-format frontend-format format \
	backend-typecheck frontend-typecheck typecheck \
	build check

help:
	@echo "Photo Sorter"
	@echo ""
	@echo "  make install      Reproduce locked environments"
	@echo "  make dev-api      Start FastAPI development server"
	@echo "  make dev-ui       Start Vite development server"
	@echo "  make test         Run all tests"
	@echo "  make lint         Run all linters"
	@echo "  make format       Format source code"
	@echo "  make typecheck    Run static type checking"
	@echo "  make build        Build frontend"
	@echo "  make check        Run the complete repository check"

install:
	cd $(BACKEND) && uv sync --frozen
	cd $(FRONTEND) && npm ci

dev-api:
	cd $(BACKEND) && uv run uvicorn photo_sorter.main:app \
		--reload \
		--host 127.0.0.1 \
		--port 8765

dev-ui:
	cd $(FRONTEND) && npm run dev

backend-test:
	cd $(BACKEND) && uv run pytest

frontend-test:
	cd $(FRONTEND) && npm test

test: backend-test frontend-test

backend-lint:
	cd $(BACKEND) && uv run ruff check .

frontend-lint:
	cd $(FRONTEND) && npm run lint

lint: backend-lint frontend-lint

backend-format:
	cd $(BACKEND) && uv run ruff format .
	cd $(BACKEND) && uv run ruff check --fix .

frontend-format:
	cd $(FRONTEND) && npm run format

format: backend-format frontend-format

backend-typecheck:
	cd $(BACKEND) && uv run mypy src tests

frontend-typecheck:
	cd $(FRONTEND) && npm run typecheck

typecheck: backend-typecheck frontend-typecheck

build:
	cd $(FRONTEND) && npm run build

check: lint typecheck test build

back-check: backend-lint backend-typecheck backend-test

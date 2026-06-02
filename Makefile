# MARS — Developer Makefile
# Usage: make <target>
# On Windows with nmake: nmake <target>

.PHONY: help install lint test run docker-build docker-up docker-down clean visualize

help:
	@echo "MARS Multi-Agent Research System"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      Install all dependencies via uv"
	@echo "  make lint         Run ruff linter"
	@echo "  make test         Run all unit tests"
	@echo "  make run          Start the Streamlit app locally"
	@echo "  make visualize    Save a visualization of the agent graph"
	@echo "  make docker-build Build the Docker image"
	@echo "  make docker-up    Start the app via docker-compose"
	@echo "  make docker-down  Stop docker-compose services"
	@echo "  make clean        Remove caches and temp files"

install:
	uv sync

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

test:
	uv run pytest tests/ -v --tb=short

test-cov:
	uv run pytest tests/ -v --tb=short --cov=. --cov-report=term-missing

run:
	uv run streamlit run app.py

docker-build:
	docker build -t mars-research-system:latest .

docker-up:
	docker compose up --build

docker-down:
	docker compose down

visualize:
	uv run python scripts/visualize_graph.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

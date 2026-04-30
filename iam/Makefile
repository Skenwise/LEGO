.PHONY: help install lint test test-integration test-e2e migrate build run docker-build docker-up docker-down clean

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

help:
	@echo "${BLUE}VaultGuard IAM Module${NC}"
	@echo ""
	@echo "${GREEN}Available commands:${NC}"
	@echo "  make install        - Install dependencies"
	@echo "  make lint           - Run linters (ruff, mypy)"
	@echo "  make test           - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-e2e       - Run end-to-end tests"
	@echo "  make test-all       - Run all tests"
	@echo "  make migrate        - Run database migrations"
	@echo "  make run            - Run development server"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-up      - Start all services (DB, Redis, IAM)"
	@echo "  make docker-down    - Stop all services"
	@echo "  make verify         - Run hexagonal isolation verification"
	@echo "  make clean          - Clean cache files"

install:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check .
	mypy core/ --ignore-missing-imports
	bandit -r core/ -ll

test:
	pytest tests/unit/ -v --cov=core --cov-report=term-missing

test-integration:
	pytest tests/integration/ -v -m integration

test-e2e:
	pytest tests/e2e/ -v -m e2e

test-all:
	pytest tests/ -v --cov=core --cov=adapters --cov-report=html

migrate:
	python scripts/run_migrations.py

run:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

verify:
	python scripts/verify_hexagonal.py

docker-build:
	docker build -t vaultguard-iam:latest .

docker-up:
	docker-compose up -d
	@echo "${GREEN}Services starting...${NC}"
	@sleep 5
	@echo "IAM API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage

docker-logs:
	docker-compose logs -f iam-dev

shell:
	docker-compose exec iam-dev /bin/bash

db-shell-profile:
	docker-compose exec profile-db psql -U profile_user -d profile_db

db-shell-auth:
	docker-compose exec auth-db psql -U auth_user -d auth_db

redis-cli:
	docker-compose exec redis redis-cli

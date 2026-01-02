.PHONY: install install-dev clean format lint test coverage docs build docker-build docker-up

# Variables
PYTHON = python3
PIP = pip3
VENV = .venv
PROJECT_NAME = pts

# Installation
install:
	@echo "Installing production dependencies..."
	$(PIP) install .

install-dev:
	@echo "Installing development dependencies..."
	$(PIP) install -r requirements-dev.txt
	pre-commit install

# Environment
clean:
	@echo "Cleaning up build artifacts and caches..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov build dist $(VENV)
	rm -f .coverage

# Code Quality
format:
	@echo "Formatting code with Black and Isort..."
	black src tests scripts
	isort src tests scripts

lint:
	@echo "Linting code with Pylint and Mypy..."
	pylint src
	mypy src

# Testing
test:
	@echo "Running tests with Pytest..."
	pytest -v

coverage:
	@echo "Running tests and generating coverage report..."
	pytest --cov=src/$(PROJECT_NAME) --cov-report=xml --cov-report=html

# Documentation
docs:
	@echo "Building documentation with MkDocs..."
	mkdocs build

# Build and Distribution
build: clean
	@echo "Building distribution packages..."
	$(PYTHON) setup.py sdist bdist_wheel

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t $(PROJECT_NAME):latest .

docker-up:
	@echo "Starting development environment with Docker Compose..."
	docker-compose up -d

# Default target
all: install-dev format lint test docs

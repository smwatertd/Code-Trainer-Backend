.PHONY: install install-dev lint lint-fix typecheck test test-down test-local test-unit test-integration test-e2e test-cov dev dev-down migrate seed-dev runners runners-build runners-down prod prod-down prod-runners prod-runners-build up pre-commit hooks _cleanup-legacy-dev _cleanup-legacy-runners

COMPOSE_DEV = docker compose -f ./docker/docker-compose.dev.yml
COMPOSE_PROD = docker compose -f ./docker/docker-compose.prod.yml
COMPOSE_TEST = docker compose -f ./docker/docker-compose.test.yml
COMPOSE_RUNNERS = docker compose -f ./docker/docker-compose.runners.yml
COMPOSE_RUNNERS_PROD = docker compose -f ./docker/docker-compose.runners.prod.yml
export BUILDX_NO_DEFAULT_ATTESTATIONS = 1
RUNNERS = python cpp pascal java csharp
RUNNERS_PROD = python cpp pascal csharp
DOCKER_BUILD_FLAGS = --provenance=false --sbom=false
LEGACY_DEV_CONTAINERS = code-trainer-dev-api code-trainer-dev-postgres code-trainer-dev-redis
LEGACY_RUNNER_CONTAINERS = code-trainer-python-runner code-trainer-cpp-runner code-trainer-pascal-runner code-trainer-java-runner code-trainer-csharp-runner

install:
	poetry install --only main

install-dev:
	poetry install
	pre-commit install

lint:
	ruff check src tests
	black --check src tests migrations

typecheck:
	mypy src

lint-fix:
	black src tests migrations
	ruff check --fix src tests

test:
	@status=0; \
	trap '$(COMPOSE_TEST) down -v --remove-orphans' EXIT; \
	$(COMPOSE_TEST) up --build --abort-on-container-exit --exit-code-from api || status=$$?; \
	exit $$status

test-down:
	$(COMPOSE_TEST) down -v --remove-orphans

test-local:
	pytest

test-unit:
	pytest tests/unit

test-integration:
	pytest tests/integration

test-e2e:
	pytest tests/e2e

test-cov:
	pytest --cov=src --cov-report=html:coverage --cov-report=xml:coverage.xml

_cleanup-legacy-dev:
	@for name in $(LEGACY_DEV_CONTAINERS); do docker rm -f "$$name" 2>/dev/null || true; done

_cleanup-legacy-runners:
	@for name in $(LEGACY_RUNNER_CONTAINERS); do docker rm -f "$$name" 2>/dev/null || true; done

dev: _cleanup-legacy-dev
	$(COMPOSE_DEV) up -d --build --remove-orphans

dev-down:
	$(COMPOSE_DEV) down --remove-orphans

prod:
	$(COMPOSE_PROD) --env-file .env up -d --build --remove-orphans

prod-down:
	$(COMPOSE_PROD) down --remove-orphans

prod-runners-build: runners-build-prod

prod-runners:
	@chmod +x ./deploy/build-runners-prod.sh
	./deploy/build-runners-prod.sh

runners-build-prod:
	@set -e; \
	for runner in $(RUNNERS_PROD); do \
	  echo "==> $${runner}_runner"; \
	  docker build $(DOCKER_BUILD_FLAGS) \
	    -f docker/runners/Dockerfile.$$runner \
	    -t $${runner}_runner \
	    .; \
	done

prod-runners-legacy: _cleanup-legacy-runners
	@set -e; \
	for runner in $(RUNNERS); do \
	  img="$${runner}_runner"; \
	  df="docker/runners/Dockerfile.$$runner"; \
	  if ! docker image inspect "$$img" >/dev/null 2>&1; then \
	    echo "==> building $$img (first time)"; \
	    docker build $(DOCKER_BUILD_FLAGS) -f $$df -t $$img .; \
	  fi; \
	done
	$(COMPOSE_RUNNERS) up -d --force-recreate --remove-orphans --no-build

up: dev runners

migrate:
	$(COMPOSE_DEV) exec -T api alembic upgrade head

seed-dev:
	$(COMPOSE_DEV) exec -T api python -m src.cli seed-dev

runners-build:
	@set -e; \
	for runner in $(RUNNERS); do \
	  echo "==> $${runner}_runner"; \
	  docker build $(DOCKER_BUILD_FLAGS) \
	    -f docker/runners/Dockerfile.$$runner \
	    -t $${runner}_runner \
	    .; \
	done

runners: _cleanup-legacy-runners
	@set -e; \
	for runner in $(RUNNERS); do \
	  img="$${runner}_runner"; \
	  df="docker/runners/Dockerfile.$$runner"; \
	  if ! docker image inspect "$$img" >/dev/null 2>&1; then \
	    echo "==> building $$img (first time)"; \
	    docker build $(DOCKER_BUILD_FLAGS) -f $$df -t $$img .; \
	  fi; \
	done
	$(COMPOSE_RUNNERS) up -d --force-recreate --remove-orphans --no-build

runners-down:
	$(COMPOSE_RUNNERS) down --remove-orphans

pre-commit:
	pre-commit run --all-files

hooks:
	pre-commit install

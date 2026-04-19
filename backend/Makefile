SHELL := /usr/bin/env bash

.PHONY: help sync install migrate makemigrations run test shell superuser clean

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make <target>\n\nTargets:\n"} /^[a-zA-Z0-9_-]+:.*##/ { printf "  %-16s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

sync: ## Install/update deps into .venv (uv.lock)
	uv sync

install: sync ## Alias for sync

migrate: ## Apply migrations
	uv run python manage.py migrate

makemigrations: ## Create migrations (when models change)
	uv run python manage.py makemigrations

run: ## Start dev server on 0.0.0.0:8000
	uv run python manage.py runserver 0.0.0.0:8000

test: ## Run tests
	uv run python manage.py test

shell: ## Django shell
	uv run python manage.py shell

superuser: ## Create Django admin user
	uv run python manage.py createsuperuser

clean: ## Remove local venv + caches (safe locally)
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf **/__pycache__

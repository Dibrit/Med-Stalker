SHELL := /usr/bin/env bash

.PHONY: help sync install run build watch test clean

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make <target>\n\nTargets:\n"} /^[a-zA-Z0-9_-]+:.*##/ { printf "  %-16s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

sync: ## Install/update frontend dependencies
	npm install

install: sync ## Alias for sync

run: ## Start Angular dev server on 0.0.0.0:4200
	npm start -- --host 0.0.0.0

build: ## Create a production build
	npm run build

watch: ## Rebuild continuously in development mode
	npm run watch

test: ## Run unit tests once
	npm test -- --watch=false

clean: ## Remove installed packages and local build caches
	rm -rf node_modules
	rm -rf .angular/cache
	rm -rf dist
	rm -rf coverage

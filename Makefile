.PHONY: help dev prod test build clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up --build

prod: ## Start production environment
	docker-compose -f docker-compose.prod.yml up --build

test: ## Run tests
	docker-compose -f docker-compose.test.yml run --rm lang-app python -m pytest

clean: ## Clean up containers and images
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

logs: ## Show logs
	docker-compose logs -f

shell: ## Open shell in running container
	docker-compose exec lang-app bash
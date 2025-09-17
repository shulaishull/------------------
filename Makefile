# Makefile for FileCompareHub

# Default target
.PHONY: help
help:
	@echo "FileCompareHub Makefile"
	@echo "Available commands:"
	@echo "  init          - Initialize data directory"
	@echo "  dev           - Start development environment"
	@echo "  prod          - Start production environment"
	@echo "  stop          - Stop all services"
	@echo "  logs          - View logs"
	@echo "  test          - Run tests"
	@echo "  clean         - Remove all containers and volumes"
	@echo "  health        - Run health check"

# Initialize data directory
.PHONY: init
init:
	@if [ -f init.sh ]; then \
		./init.sh; \
	else \
		powershell -ExecutionPolicy Bypass -File init.ps1; \
	fi

# Start development environment
.PHONY: dev
dev: init
	docker-compose up --build

# Start production environment
.PHONY: prod
prod: init
	docker-compose -f docker-compose.prod.yml up --build -d

# Stop all services
.PHONY: stop
stop:
	docker-compose -f docker-compose.prod.yml down

# View logs
.PHONY: logs
logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Run tests
.PHONY: test
test:
	docker-compose -f docker-compose.prod.yml exec backend python -m pytest
	docker-compose -f docker-compose.prod.yml exec frontend npm test

# Remove all containers and volumes
.PHONY: clean
clean:
	docker-compose -f docker-compose.prod.yml down -v

# Run health check
.PHONY: health
health:
	@if [ -f health-check.sh ]; then \
		./health-check.sh; \
	else \
		powershell -ExecutionPolicy Bypass -File health-check.ps1; \
	fi
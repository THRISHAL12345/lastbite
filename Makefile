.PHONY: up down test build lint seed
up:
	docker compose up --build -d
down:
	docker compose down
test:
	cd backend && ../.venv/bin/pytest -v
	cd frontend && npm test
build:
	cd frontend && npm ci && npm run build
lint:
	helm lint helm/relaydesk
	terraform fmt -check -recursive terraform
	docker compose config --quiet
seed:
	python3 scripts/seed.py

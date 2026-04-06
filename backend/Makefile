.PHONY: up down logs test shell migrate lint db-shell diagnose

up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f backend

test:
	docker-compose exec backend pytest -v --cov=app

shell:
	docker-compose exec backend bash

migrate:
	docker-compose exec backend alembic upgrade head

lint:
	docker-compose exec backend ruff check .

db-shell:
	docker-compose exec postgres psql -U postgres -d lqy_db

diagnose:
	python diagnose.py

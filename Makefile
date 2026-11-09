.PHONY: backend-install backend-run backend-test backend-lint backend-format alembic-current backend-validate validate

RUFF := backend/.venv/bin/ruff

backend-install:
	cd backend && .venv/bin/python -m pip install -e ".[dev]"

backend-run:
	cd backend && .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --no-access-log

backend-test:
	cd backend && .venv/bin/python -m pytest -v

backend-lint:
	$(RUFF) check backend/app backend/tests backend/migrations
	$(RUFF) format --check backend/app backend/tests backend/migrations

backend-format:
	$(RUFF) check --fix backend/app backend/tests backend/migrations
	$(RUFF) format backend/app backend/tests backend/migrations

alembic-current:
	cd backend && .venv/bin/alembic current

backend-validate:
	$(RUFF) check backend/app backend/tests backend/migrations
	$(RUFF) format --check backend/app backend/tests backend/migrations
	cd backend && .venv/bin/python -m pip check
	cd backend && .venv/bin/python -m pytest -v
	cd backend && .venv/bin/alembic current

validate: backend-validate

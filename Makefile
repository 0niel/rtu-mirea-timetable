include .env
export


# Migration
migrate:
	docker compose exec backend alembic upgrade head


## Format all
fmt: format
format: isort black


## Check code quality
chk: check
lint: check
check: flake black_check isort_check

mypy:
	mypy app tests


## Sort imports
isort:
	isort app tests worker

isort_check:
	isort --check-only app tests worker


## Format code
black:
	black --config pyproject.toml app tests worker

black_check:
	black --config pyproject.toml --diff --check app tests worker


# Check pep8
flake:
	flake8 --config .flake8 app tests worker

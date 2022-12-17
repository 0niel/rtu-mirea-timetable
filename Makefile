export
## Connect to container
connect:
	docker-compose exec backend bash

## Format all
fmt: format
format:
	isort --force-single-line-imports app
	isort --force-single-line-imports tests
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --exclude=__init__.py
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place tests --exclude=__init__.py
	black app tests
	isort app tests


## Check code quality
chk: check
lint: check
check: flake black_check isort_check


## Tests
tests: test
test:
	pytest --asyncio-mode=strict -v

cov: coverage
coverage:
	coverage run -m pytest --asyncio-mode=strict -v && coverage report -m


## Sort imports
isort:
	isort app tests

isort_check:
	isort --check-only app tests


## Format code
black:
	black app tests

black_check:
	black --config pyproject.toml --diff --check app tests


# Check pep8
flake:
	flake8 --config .flake8 app tests
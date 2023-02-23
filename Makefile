export
## Connect to container
connect:
	docker-compose exec backend bash

## Format all
fmt: format
format:
	isort --force-single-line-imports app
	isort --force-single-line-imports tests
	isort --force-single-line-imports worker
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --exclude=__init__.py
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place tests --exclude=__init__.py
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place worker --exclude=__init__.py
	black app tests worker
	isort app tests worker


## Check code quality
chk: check
lint: check
check: flake black_check isort_check


## Tests
tests: test
test:
	pytest --asyncio-mode=strict -v

## Sort imports
isort:
	isort app tests worker

isort_check:
	isort --check-only app tests worker


## Format code
black:
	black app tests worker

black_check:
	black --diff --check app tests worker


# Check pep8
flake:
	flake8 app tests worker
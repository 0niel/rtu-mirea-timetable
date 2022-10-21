.PHONY: fix
fix:
	black app
	isort app

.PHONY: flake
flake:
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app

.PHONY: lint
lint:
	black app
	isort app

.PHONY: test
test:
	pytest app

.DEFAULT_GOAL :=
# include .env
# export

# files_to_fmt ?= app # enumeration of * .py file storage or folders is required.
# files_to_check ?= app # enumeration of * .py files storage or folders is required.

# # Default target
# .DEFAULT_GOAL := run

# # Build and Run docker containers
# docker_up:
#   docker-compose up --build -d

# # Run application
# run:
#   uvicorn main:app --host localhost --reload --port ${BACKEND_SERVER_PORT} --workers 2

# ## Format all
# fmt: format
# format: remove_imports isort black docformatter

# ## Check code quality
# chk: check
# lint: check
# check: flake8 black_check docformatter_check

# # ## Migrate database
# # migrate:
# #   python -m scripts.migrate

# # ## Rollback migrations in database
# # migrate-rollback:
# #   python -m scripts.migrate --rollback

# # migrate-reload:
# #   python -m scripts.migrate --reload

# ## Remove unused imports
# remove_imports:
#   autoflake -ir --remove-unused-variables \
#     --ignore-init-module-imports \
#     --remove-all-unused-imports \
#     ${files_to_fmt}

# ## Sort imports
# isort:
#   isort ${files_to_fmt}

# ## Format code
# black:
#   black ${files_to_fmt}

# ## Check code formatting
# black_check:
#   black --check ${files_to_check}

# ## Format docstring PEP 257
# docformatter:
#   docformatter -ir ${files_to_fmt}

# ## Check docstring formatting
# docformatter_check:
#   docformatter -cr ${files_to_check}

# ## Check pep8
# flake8:
#   flake8 ${files_to_check}

# ## Check typing
# mypy:
#   mypy ${files_to_check}
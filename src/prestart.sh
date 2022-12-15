#!/usr/bin/env sh

# Let the DB start
sleep 10;

# Run migrations
alembic upgrade head

#!/bin/bash

echo "$ENV"

# Let the DB start
# sleep 10;

# Run migrations
alembic upgrade head;

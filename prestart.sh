#!/bin/bash

echo "$ENV"

# Run migrations
alembic upgrade head;
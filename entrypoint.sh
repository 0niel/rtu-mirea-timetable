#!/bin/bash

echo "$ENV"

if [ "$ENV" == "development" ]; then
  alembic upgrade head
fi

python runserver.py
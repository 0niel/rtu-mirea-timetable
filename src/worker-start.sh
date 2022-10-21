 #! /usr/bin/env bash
set -e

celery -A app.worker worker --beat -l info -Q main-queue -c 1
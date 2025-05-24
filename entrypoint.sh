#!/bin/sh

set -e

echo "Waiting for postgres..."

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting Uvicorn server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 "$@"

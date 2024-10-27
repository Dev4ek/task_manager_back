#!/bin/sh

# Wait for Redis and Postgres to be available
echo "Waiting for Redis and Postgres to be available..."
while ! nc -z redis 6379; do
  sleep 1
done

while ! nc -z postgres 5432; do
  sleep 1
done

# while ! nc -z elasticsearch 9200; do
#   sleep 1
# done

# # Start the Celery worker
# echo "Starting Celery worker..."
# celery -A api.tasks.config.celery worker --loglevel=info &

# Wait a bit to ensure Celery has started
sleep 5

# Start FastAPI application
echo "Starting FastAPI application..."
exec python3 main.py

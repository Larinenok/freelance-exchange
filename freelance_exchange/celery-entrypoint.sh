#!/bin/sh

echo "Waiting for Redis..."
/app/freelance_exchange/wait-for-it.sh redis 6379 60

echo "Starting Celery worker..."
celery -A freelance_exchange worker --loglevel=info
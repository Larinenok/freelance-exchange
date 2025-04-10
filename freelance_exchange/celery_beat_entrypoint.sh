#!/bin/sh

# Ожидаем, пока Redis не станет доступен
echo "Waiting for Redis..."
/app/freelance_exchange/wait-for-it.sh redis_container 6379 60

# Запускаем Celery Beat
echo "Starting Celery beat..."
celery -A freelance_exchange beat --loglevel=info

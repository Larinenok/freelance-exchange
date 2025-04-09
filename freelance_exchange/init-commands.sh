#!/bin/bash
rm -rf /app/freelance_exchange/static/*
python3 manage.py collectstatic --noinput
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput
python3 manage.py initadmin
daphne -b 0.0.0.0 -p 8001 freelance_exchange.asgi:application

#! /bin/bash

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
python3 manage.py initadmin
# uwsgi --ini /etc/uwsgi.ini
# python3 manage.py runserver 0.0.0.0:8001
daphne -b 0.0.0.0 -p 8001 freelance_exchange.asgi:application

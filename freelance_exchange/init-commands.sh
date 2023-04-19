#! /bin/bash

python3 manage.py collectstatic --noinput
python3 manage.py migrate
uwsgi --ini /etc/uwsgi.ini

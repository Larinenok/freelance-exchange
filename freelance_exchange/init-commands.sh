#! /bin/bash

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
python3 manage.py initadmin
uwsgi --ini /etc/uwsgi.ini

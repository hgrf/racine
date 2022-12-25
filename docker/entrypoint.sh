#! /usr/bin/env sh
set -e

/uwsgi-nginx-flask-entrypoint.sh

if [ ! -d "/app/app/static/bootstrap" ]; then
    git clone -b 3.3.7.1 --depth 1 https://github.com/mbr/flask-bootstrap.git /flask-bootstrap
    mv /flask-bootstrap/flask_bootstrap/static /app/app/static/bootstrap
    rm -rf /flask-bootstrap
fi

python manage.py db upgrade

exec "$@"

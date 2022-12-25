#! /usr/bin/env sh
set -e

/uwsgi-nginx-flask-entrypoint.sh

if [ ! -d "/app/app/static/bootstrap" ]; then
    mv /flask-bootstrap/flask_bootstrap/static /app/app/static/bootstrap
    rm -rf /flask-bootstrap
fi

exec "$@"

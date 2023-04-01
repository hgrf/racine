#! /usr/bin/env sh
set -e

python manage.py db upgrade

if [ -f /etc/nginx/ssl/server.key ] \
        && [ -f /etc/nginx/ssl/server.crt ] \
        && [ -f /etc/nginx/ssl/server_name.txt ]; then
    echo "SSL enabled"
    # override nginx config from tiangolo/uwsgi-nginx-flask Docker image
    cp /app/app/nginx.conf /etc/nginx/conf.d/nginx.conf
    sed -i "s/localhost/$(cat /etc/nginx/ssl/server_name.txt)/g" /etc/nginx/conf.d/nginx.conf
fi

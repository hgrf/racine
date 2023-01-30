#! /usr/bin/env sh
set -e

python manage.py db upgrade

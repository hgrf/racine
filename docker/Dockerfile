# based on https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu-20-04
# TODO: might want to use -slim as base image of tiangolo/uwsgi-nginx instead to make it smaller
# see also: https://medium.com/swlh/alpine-slim-stretch-buster-jessie-bullseye-bookworm-what-are-the-differences-in-docker-62171ed4531d
FROM tiangolo/uwsgi-nginx-flask:python3.10 AS racine-base

ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static

ENV UWSGI_INI /app/docker/uwsgi.ini

COPY ./Makefile /app/Makefile
COPY ./version.csv /app/version.csv
# TODO: is there any way to auto-detect these?
COPY ./.github/workflows/module.mk /app/.github/workflows/module.mk
COPY ./app/static/module.mk /app/app/static/module.mk
COPY ./desktop/module.mk /app/desktop/module.mk
COPY ./docker/module.mk /app/docker/module.mk
COPY ./docs/module.mk /app/docs/module.mk
COPY ./site/module.mk /app/site/module.mk
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements-dev.txt /app/requirements-dev.txt

RUN apt update && \
    apt install -y default-jre && \
    apt install -y npm && \
    apt install -y watchman && \
    npm install -g n && \
    n stable && \
    make install-dependencies PIP_OPTIONS=--no-cache-dir

# replace prestart script from base image
COPY ./docker/prestart.sh /app/prestart.sh

# Run the start script provided by the parent image tiangolo/uwsgi-nginx.
# It will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Supervisor, which in turn will start Nginx and uWSGI
CMD ["/start.sh"]

FROM racine-base AS racine

ENV FLASK_CONFIG production

COPY ./app /app/app/
COPY ./migrations /app/migrations/
COPY ./docker/uwsgi.ini /app/docker/uwsgi.ini

COPY ./Makefile /tmp/app_static/Makefile
COPY ./version.csv /tmp/app_static/version.csv
# TODO: is there any way to auto-detect these?
COPY ./.github/workflows/module.mk /tmp/app_static/.github/workflows/module.mk
COPY ./app/static/module.mk /tmp/app_static/app/static/module.mk
COPY ./desktop/module.mk /tmp/app_static/desktop/module.mk
COPY ./docker/module.mk /tmp/app_static/docker/module.mk
COPY ./docs/module.mk /tmp/app_static/docs/module.mk
COPY ./site/module.mk /tmp/app_static/site/module.mk
COPY ./patches /tmp/app_static/patches
COPY ./js /tmp/app_static/js
COPY ./app/static/icons /tmp/app_static/app/static/icons

RUN cd /tmp/app_static && \
    mkdir -p app/static/images && \
# for racine.log
    mkdir -p /app/data && \
# also for racine.log
    mkdir -p data && \
    make install-js-dependencies && \
    rm -rf /app/data && \
    cp -r /tmp/app_static/app/static /app/app/ && \
    rm -rf /tmp/app_static

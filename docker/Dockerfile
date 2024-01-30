# based on https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu-20-04
# TODO: might want to use -slim as base image of tiangolo/uwsgi-nginx instead to make it smaller
# see also: https://medium.com/swlh/alpine-slim-stretch-buster-jessie-bullseye-bookworm-what-are-the-differences-in-docker-62171ed4531d
FROM tiangolo/uwsgi-nginx-flask:python3.10 AS racine-base

LABEL maintainer="Holger Graef"
LABEL org.opencontainers.image.authors="Holger Graef"

ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static

ENV UWSGI_INI /app/docker/uwsgi.ini

COPY ./Makefile /app/Makefile
COPY ./version.csv /app/version.csv
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements-dev.txt /app/requirements-dev.txt

RUN make install-dependencies PIP_OPTIONS=--no-cache-dir

# replace prestart script from base image
COPY ./docker/prestart.sh /app/prestart.sh

# Run the start script provided by the parent image tiangolo/uwsgi-nginx.
# It will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Supervisor, which in turn will start Nginx and uWSGI
CMD ["/start.sh"]

FROM racine-base AS racine-dev

RUN apt update && \
    apt install -y default-jre && \
    apt install -y npm && \
    apt install -y watchman && \
    rm -rf /var/lib/apt/lists/* && \
    npm install -g n && \
    n stable

FROM racine-base AS racine

ENV FLASK_CONFIG production

COPY ./app /app/app/
COPY ./migrations /app/migrations/
COPY ./docker/uwsgi.ini /app/docker/uwsgi.ini

COPY ./app/static /app/app/static

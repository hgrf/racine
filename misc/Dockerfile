# based on https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu-20-04
# TODO: might want to use -slim as base image of tiangolo/uwsgi-nginx instead to make it smaller
# see also: https://medium.com/swlh/alpine-slim-stretch-buster-jessie-bullseye-bookworm-what-are-the-differences-in-docker-62171ed4531d
FROM tiangolo/uwsgi-nginx-flask:python3.10 AS msm-base

ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static

RUN echo "Current path: $PWD"

COPY ./Makefile /app/Makefile
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements-dev.txt /app/requirements-dev.txt

RUN make install-dependencies PIP_OPTIONS=--no-cache-dir


FROM msm-base AS msm

COPY ./app /app/app/
COPY ./migrations /app/migrations/
COPY ./manage.py /app/
COPY ./uwsgi.ini /app/

RUN make copy-bootstrap

RUN mkdir /app/database
RUN mkdir /app/uploads
RUN python manage.py db upgrade

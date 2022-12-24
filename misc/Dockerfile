# based on https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu-20-04

FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine AS msm-base

ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static

RUN echo "Current path: $PWD"

RUN apk --update add bash nano git

COPY ./Makefile /app/Makefile
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements-dev.txt /app/requirements-dev.txt
# for Pillow (see also https://github.com/python-pillow/Pillow/issues/1763) and other python packages that require building
RUN apk add build-base linux-headers zlib-dev jpeg-dev
RUN make install-dependencies

FROM msm-base AS msm

COPY ./app /app/app/
COPY ./migrations /app/migrations/
COPY ./manage.py /app/
COPY ./misc/uwsgi.ini /app/

RUN make copy-bootstrap

RUN mkdir /app/database
RUN mkdir /app/uploads
RUN python manage.py db upgrade

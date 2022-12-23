# based on https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu-20-04

FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static

RUN echo "Current path: $PWD"

RUN apk --update add bash nano git

COPY ./Makefile /Makefile
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements-dev.txt /app/requirements-dev.txt
# for Pillow (see also https://github.com/python-pillow/Pillow/issues/1763) and other python packages that require building
RUN apk add build-base linux-headers zlib-dev jpeg-dev
RUN make install-dependencies

COPY ./app /app/app/
COPY ./migrations /app/migrations/
COPY ./manage.py /app/
COPY ./uwsgi.ini /app/

RUN git clone -b 3.3.7.1 --depth 1 https://github.com/mbr/flask-bootstrap.git
RUN ls flask-bootstrap
RUN mv ./flask-bootstrap/flask_bootstrap/static /app/app/static/bootstrap
RUN rm -rf flask-bootstrap

RUN mkdir /app/database
RUN mkdir /app/uploads
RUN python manage.py db upgrade

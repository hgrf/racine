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

# here we just make flask-bootstrap available, it is copied later, because the dev image
# has to place it in the mounted volume
RUN git clone -b 3.3.7.1 --depth 1 https://github.com/mbr/flask-bootstrap.git /flask-bootstrap

# Move the base entrypoint to reuse it
RUN mv /entrypoint.sh /uwsgi-nginx-flask-entrypoint.sh
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Run the start script provided by the parent image tiangolo/uwsgi-nginx.
# It will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Supervisor, which in turn will start Nginx and uWSGI
CMD ["/start.sh"]

FROM msm-base AS msm

COPY ./app /app/app/
COPY ./migrations /app/migrations/
COPY ./manage.py /app/
COPY ./uwsgi.ini /app/

RUN mkdir /app/database
RUN mkdir /app/uploads
RUN python manage.py db upgrade

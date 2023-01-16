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

RUN apt update
RUN apt install -y dos2unix default-jre

RUN make install-dependencies PIP_OPTIONS=--no-cache-dir

COPY ./Makefile /tmp/app_static/Makefile
COPY ./requirements.txt /tmp/app_static/requirements.txt
COPY ./patches /tmp/app_static/patches

RUN cd /tmp/app_static && \
    mkdir -p app/static && \
    make install-js-dependencies

# remove prestart script from base image
RUN rm /app/prestart.sh

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

ENV FLASK_CONFIG production

COPY ./app /app/app/
COPY ./migrations /app/migrations/
COPY ./manage.py /app/
COPY ./uwsgi.ini /app/

RUN cp -r /tmp/app_static/app/static /app/app/

COPY ./patches/generate-api-spec.py /app/patches/generate-api-spec.py
COPY ./patches/api.yaml /app/patches/api.yaml
COPY ./patches/rollup.config.js /app/patches/rollup.config.js

RUN apt install -y npm
RUN npm install -g n
RUN n stable
RUN mkdir build && \
    make api-client

# RUN rm -rf /tmp/app_static

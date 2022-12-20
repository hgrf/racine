# based on https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu-20-04

FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
RUN apk --update add bash nano git
ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static
COPY ./requirements.txt /var/www/requirements.txt
# for Pillow (see also https://github.com/python-pillow/Pillow/issues/1763) and other python packages that require building
RUN apk add build-base linux-headers zlib-dev jpeg-dev
RUN pip install --upgrade pip
RUN pip install -r /var/www/requirements.txt
RUN pip install pytest

COPY . /app/

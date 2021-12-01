FROM python:3.8-alpine3.14 AS base

LABEL maintainer="Clovis Djiometsa <clovis@dnclovis.com>"

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache bash wget libpq icu-libs geos gdal&& \
    wget https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py && \
    python get-poetry.py --version 1.1.11 && \
    apk del wget

# Install and configure virtualenv
RUN pip install virtualenv==20.10.0
ENV VIRTUAL_ENV=/app/.virtualenv
ENV PATH=$VIRTUAL_ENV/bin:/root/.poetry/bin:$PATH

# Initialize app dir and entrypoint scripts
RUN mkdir /app
WORKDIR /app
COPY entrypoints/* /
RUN chmod +x /*.sh
ENTRYPOINT ["/entrypoint.sh"]

## Image with system dependencies for building ##
## =========================================== ##
FROM base AS build

# Essential packages for building python packages
RUN apk add --no-cache build-base git libffi-dev linux-headers jpeg-dev freetype-dev postgresql-dev su-exec

COPY . /app/

## Image with additional dependencies for local docker usage ##
## ========================================================= ##
FROM build as local
RUN chmod -R 777 /root/  ## Grant all local users access to poetry
RUN apk add gdb

# start from an official image
FROM python:3.7.5-slim-buster

RUN mkdir -p /opt/services/django-git/ && mkdir -p /opt/test/django-git/
ADD pytradebot/ /opt/services/django-git/
ADD memcached.conf /etc/memcached.conf
ARG DEBIAN_FRONTEND=noninteractive

# install our two dependencies
RUN apt-get update && apt-get install -yq --no-install-recommends build-essential wget pkg-config libpq-dev python-dev memcached \
   && usermod -g www-data memcache \
   && cd /opt/services/django-git/ \
   && pip install --upgrade pip && pip install --default-timeout=100 -r requirements.txt \
   && apt-get remove -y --purge build-essential && apt-get autoremove -y && apt-get clean -y \
   && rm -rf /var/lib/apt/lists/*

# Timezone
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /opt/services/django-git/

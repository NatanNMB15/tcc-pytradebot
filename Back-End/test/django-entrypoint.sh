#!/bin/bash
service memcached start && \
cd /opt/test/pytradebot/ && \
pip install --upgrade pip && pip install --default-timeout=100 -r requirements.txt && \
python manage.py collectstatic --noinput && python manage.py makemigrations --noinput && python manage.py migrate --noinput && python manage.py test --noinput && \
python manage.py initadmin --email $DJANGO_EMAIL --password $DJANGO_PASSWORD --noinput && \
gunicorn pytradebot.wsgi --workers=3 --worker-class=gevent --worker-connections=1000 --config gunicorn_config.py -b 0.0.0.0:80
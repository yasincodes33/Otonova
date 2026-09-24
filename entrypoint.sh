#!/bin/sh
set -e

echo ">> Migrations uygulanıyor..."
python manage.py migrate --noinput

echo ">> Sunucu başlatılıyor..."
exec gunicorn Otonova.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --preload

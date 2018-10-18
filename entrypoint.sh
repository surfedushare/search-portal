#!/bin/bash
set -e
if [ x"$DO_DJANGO_INIT" != x ]; then
  python manage.py collectstatic --noinput
  python manage.py migrate
fi
exec "$@"

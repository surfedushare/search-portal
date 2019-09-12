#!/usr/bin/env bash

# Exit immediately on error
set -e

# We're serving static files through Whitenoise
# See: http://whitenoise.evans.io/en/stable/index.html#
# If you doubt this decision then read the "infrequently asked question" section for details
# Here we gather static files that get served through uWSGI if they don't exist
if [[ ! -d "static" ]]; then
    ./manage.py collectstatic --noinput
fi

# Executing the normal commands
exec "$@"

#!/usr/bin/env bash


# Exit immediately on error
set -e


# Links the correct uWSGI configuration files based on the project
rm -f /usr/src/app/uwsgi/sites-enabled/*
if [ "$APPLICATION_PROJECT" == "nppo" ]
then
  ln -s /usr/src/app/uwsgi/sites-available/publinova_nl.ini /usr/src/app/uwsgi/sites-enabled/publinova_nl.ini
else
  ln -s /usr/src/app/uwsgi/sites-available/edusources_nl.ini /usr/src/app/uwsgi/sites-enabled/edusources_nl.ini
  ln -s /usr/src/app/uwsgi/sites-available/mbo_edusources_nl.ini /usr/src/app/uwsgi/sites-enabled/mbo_edusources_nl.ini
fi


# Installs local search-client repo during development when available
if [ "$POL_DJANGO_DEBUG" == "1" ]  && [ -e "/usr/src/search_client/setup.py" ] && \
    [ $(pip show search_client | grep "Location:" | awk -F "/" '{print $NF}') == "site-packages" ]
then
    echo "Replacing search_client installation with editable version"
    pip uninstall -y search_client
    pip install -e /usr/src/search_client
fi


# Executing the normal commands
exec "$@"

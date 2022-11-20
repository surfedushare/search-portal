#!/usr/bin/env bash


# Exit immediately on error
set -e


# Handles editable Python packages
# Convenient when having to update Datagrowth for this project
rm /usr/src/app/uwsgi/sites-enabled/*
if [ "$APPLICATION_PROJECT" == "nppo" ]
then
  ln -s /usr/src/app/uwsgi/sites-available/publinova_nl.ini /usr/src/app/uwsgi/sites-enabled/publinova_nl.ini
else
  ln -s /usr/src/app/uwsgi/sites-available/edusources_nl.ini /usr/src/app/uwsgi/sites-enabled/edusources_nl.ini
  ln -s /usr/src/app/uwsgi/sites-available/mbo_edusources_nl.ini /usr/src/app/uwsgi/sites-enabled/mbo_edusources_nl.ini
fi


# Executing the normal commands
exec "$@"

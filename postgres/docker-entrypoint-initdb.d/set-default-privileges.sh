#!/usr/bin/env bash


set -e


psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "edushare" -f docker-entrypoint-initdb.d/set-default-privileges.tpl
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "harvester" -f docker-entrypoint-initdb.d/set-default-privileges.tpl

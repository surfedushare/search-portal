#!/usr/bin/env bash


set -e


psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    CREATE USER django WITH ENCRYPTED PASSWORD '${POSTGRES_PASSWORD}';
    ALTER USER django CREATEDB;

EOSQL

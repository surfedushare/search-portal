#!/usr/bin/env bash


# Exit immediately on error
set -e


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

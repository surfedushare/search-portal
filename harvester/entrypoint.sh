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


# Check for AWS credentials on localhost
# If the credentials are not available stop loading secrets to prevent errors
if [ "$APPLICATION_MODE" == "localhost" ] && [ ! -e "/home/app/.aws/credentials" ]; then
    echo "Not loading AWS secrets on localhost, because ~/.aws/credentials is missing. Errors may occur at runtime."
    export POL_AWS_LOAD_SECRETS=0
    unset AWS_PROFILE
fi
# Executing the normal commands
exec "$@"

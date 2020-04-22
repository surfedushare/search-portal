#!/usr/bin/env bash

# Indicate to the application it's running outside of a container
export APPLICATION_CONTEXT=host

# Load environment variables similar to how docker-compose does it
export $(cat .env | xargs)

# Activate virtual environment
source venv/bin/activate

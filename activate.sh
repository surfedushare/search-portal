#!/usr/bin/env bash


# Load environment variables similar to how docker-compose does it
export $(cat .env | xargs)

# Activate virtual environment
source venv/bin/activate

now = $(shell date +"%Y-%m-%d")


integration-tests:
	docker-compose run --rm -e DJANGO_POSTGRES_USER=postgres -e DJANGO_POSTGRES_PASSWORD=qwerty service python manage.py test --settings=surf.settings.tests --nomigrations $(filter)

backup-db:
	docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) pg_dump -h localhost -U postgres -c edushare > edushare.${now}.postgres.sql

import-db:
	cat $(backup) | docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) psql -h localhost -U postgres edushare

start-services:
	docker-compose -f docker-compose.yml up

stop-services:
	docker-compose -f docker-compose.yml down

run-service-container:
	# Starts the main service container outside of docker-compose orchestration
	# This is useful for allowing debuggers to work while running UWSGI
	docker-compose run --service-ports service

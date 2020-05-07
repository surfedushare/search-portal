now = $(shell date +"%Y-%m-%d")


integration-tests:
	docker-compose run --rm -e DJANGO_POSTGRES_USER=postgres -e DJANGO_POSTGRES_PASSWORD=qwerty service python manage.py test --settings=surf.settings.tests --nomigrations $(filter)

backup-db:
	docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) pg_dump -h localhost -U postgres -c edushare > edushare.${now}.postgres.sql

import-db:
	cat $(backup) | docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) psql -h localhost -U postgres edushare

start-db:
	docker-compose -f docker-compose.yml up

stop-db:
	docker-compose -f docker-compose.yml down

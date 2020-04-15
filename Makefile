now = $(shell date +"%Y-%m-%d")


integration-tests:
	docker-compose run --rm -e DJANGO_POSTGRES_USER=surf -e DJANGO_POSTGRES_PASSWORD=qwerty service python manage.py test --settings=surf.settings.tests --nomigrations $(filter)

backup-db:
	docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) pg_dump -h localhost -U surf -c surf > edushare.${now}.postgres.sql

import-db:
	cat $(backup) | docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) psql -h localhost -U surf surf

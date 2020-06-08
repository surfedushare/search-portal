backup-db:
	docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) pg_dump -h localhost -U postgres -c edushare > edushare.${now}.postgres.sql

import-db:
	cat $(backup) | docker exec -i $(shell docker ps -qf label=nl.surfcatalog.db) psql -h localhost -U postgres edushare

run-service-container:
	# Starts the main service container outside of docker-compose orchestration
	# This is useful for allowing debuggers to work while running UWSGI
	cd ..
	docker-compose run --service-ports service

run-django:
	while true; do python manage.py runserver; sleep 2; done

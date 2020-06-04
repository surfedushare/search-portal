now = $(shell date +"%Y-%m-%d")


integration-tests:
	docker-compose run --rm -e DJANGO_POSTGRES_USER=postgres -e DJANGO_POSTGRES_PASSWORD=qwerty service python manage.py test --settings=surf.settings.tests --nomigrations $(filter)

start-services:
	docker-compose -f docker-compose.yml up

stop-services:
	docker-compose -f docker-compose.yml down

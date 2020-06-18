now = $(shell date +"%Y-%m-%d")


start-services:
	docker-compose -f docker-compose.yml up

stop-services:
	docker-compose -f docker-compose.yml down

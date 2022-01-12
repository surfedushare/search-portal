run-django:
	while true; do python manage.py runserver 8888; sleep 2; done

run-celery:
	watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A harvester worker --loglevel=INFO

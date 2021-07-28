run-django:
	while true; do python manage.py runserver; sleep 2; done

run-celery:
	watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A harvester worker --loglevel=INFO

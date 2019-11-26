media-to-local:
	rsync -zrthv --progress $(remote):/volumes/surf/media .

media-to-remote:
	rsync -zrthv --progress media $(remote):/volumes/surf/

tests:
    docker-compose -f docker-compose-local.yml run --rm backend python manage.py test --settings=surf.settings.tests --nomigrations

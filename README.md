# SURF Catalog backend

This repository contains backend for SURF Catalog. It is written on
Python 3.6 and is based on Django Framework.

REST API documentation is in the file `api.apib`.

# Overview

SURF Catalog backend provides following functionality:

* API methods for user authentication via SURFconext OpenID Connect
authentication flow. This code is implemented in Django
application `users` (`surf/apps/users`)

* API methods to work with EduRep materials and collections (searching,
setting ratings and applauds for materials, managing collections of
materials). This code is implemented in Django application `materials`
(`surf/apps/materials`)

* API methods to manage themes. This code is implemented in Django
application `themes` (`surf/apps/themes`)

* API methods to manage user defined filters. This code is implemented
in Django application `filters` (`surf/apps/filters`)

* API methods to manage communities related to SURFconext Teams.
This code is implemented in Django application `communities`
(`surf/apps/communities`)

* API methods to get some statistics information about service.
This code is implemented in Django application `stats`
(`surf/apps/stats`)

Django application has next structure:

* `migrations/` - the package with DB migration scripts

* `apps.py` - module with application configuration

* `models.py` - module with application entity models

* `admin.py` - module with classes for Django admin

* `views.py` - module with views for REST API methods

* `serializers.py` - module with serializers for views

* `filters.py` - module with filters for views

* `utils.py` - module with some common functions

API clients to EduRep API, SURFconext API are implemented in packages
`surf/vendor/edurep` and `surf/vendor/surfconext`

# Installation

You can install and run application locally by using docker
and docker-compose.

* Install docker according to the
[manuals](https://docs.docker.com/install/overview/) from official site

* Install docker-compose according to the
[manual](https://docs.docker.com/compose/install/#install-compose)

* Clone the repository to local directory:

```sh
git clone git@github.com:surfedushare/surf-backend.git
cd surf-backend
```

* Copy ``.env.example`` to ``.env`` and adjust where needed

* Copy ``surf/settings/local.py.template`` to ``surf/settings/local.py`` and adjust where needed

* Create virtual environment for application and activate it:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

* Install python libraries for docker and docker-compose to virtual
environment:

```sh
pip install docker docker-compose
```

* Run application

```sh
docker-compose up
```

* Create the first Django admin of the application

```sh
docker-compose run --rm backend python manage.py createsuperuser
```

# References

All project requirements are specified in files
`requirements/requirements.dev.txt` (for staging environment) and
`requirements/requirements.prod.txt` (for production environment)

* Requires [Django](https://www.djangoproject.com/)
* Requires [Django JET](https://github.com/geex-arts/django-jet)
* Requires [Django REST Framework](http://www.django-rest-framework.org/)
* Requires [Django CORS Headers](https://github.com/ottoyiu/django-cors-headers)
* Requires [Django CORS Middleware](https://github.com/zestedesavoir/django-cors-middleware/)
* Requires [Django Filter](https://github.com/carltongibson/django-filter/)
* Requires [Psycopg](http://initd.org/psycopg/)
* Requires [Requests](https://github.com/requests/requests)
* Requires [PyOidc](https://github.com/rohe/pyoidc)
* Requires [Pillow](https://github.com/python-pillow/Pillow)

# Surf Catalog backend

This repository contains backend for Surf Catalog. It is written on
Python 3 and is based on Django Framework.

REST API documentation is in the file `api.apib`.

# Installation

You can install and run application locally by using docker
and docker-compose.

* Clone the repository to local directory:

```sh
git clone git@github.com:surfedushare/surf-backend.git
cd surf-backend
```

* Create file for settings `local.py` in directory `surf/settings/`
according to template file `surf/settings/local.py.template`

* Create virtual environment for application and activate it:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

* Install docker and docker-compose:

```sh
pip install docker docker-compose
```

* Run application

```sh
sudo docker-compose -f docker-compose-local.yml up -d
```

# References

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

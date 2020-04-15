Search Portal
=============

A search service for finding open access higher education learning materials.

The repo consists of a frontend and a backend. The frontend is called ``portal`` and is a Vue SPA. 
The backend is named ``service``, which is mostly a REST API, but also serves the frontend SPA and Django admin pages.


Prerequisites
-------------

This project uses ``Python3``, ``npm``, ``Docker`` and ``docker-compose``.
Make sure they are installed on your system before installing the project.


Installation
------------

The local setup is made in such a way that you can run the project inside and outside of containers.
It can be convenient to run some code for inspection outside of containers.
To stay close to the production environment it works well to run the project in containers.
External services like the database run in containers so it's always necessary to use Docker.

#### Backend


To install the backend you'll need to first setup a local environment on a host machine with:

```bash
python3 -m venv venv
source activate.sh
pip install --upgrade pip
pip install -r service/requirements.txt
```

Then copy the ``.env.example`` file to ``.env`` and update the variable values to fit your system.
When you're running the project locally in containers you'll only need to provide your Elastic Search credentials.

If you want to run the project outside of a container please add ``DJANGO_POSTGRES_HOST=127.0.0.1``
or add ``127.0.0.1 postgres`` to your hosts file in order for the service to pickup the database.

After this you can setup your database with the following commands:

```bash
docker-compose up --build
source activate.sh  # perhaps redundant, already activated above
cd service
python manage.py migrate
python manage.py createsuperuser
```

This should have setup your database for the most part.
Unfortunately due to historic reasons there is a lot of configuration going on in the database.
So it's wise to get a production dump and import it to your system.
Please ask somebody to provide it to you and place it inside ``postgres/dumps``

After you've done this you can run:

```bash
make import-db backup=postgres/dumps/<dump-file-name>.sql
```


#### Frontend

Installation of the frontend is a lot more straightforward than the backend:

```bash
cd portal
npm install
```

Search Portal Service
=====================

A REST API build with Django and Django Rest Framework.
There is an admin available to inspect the data.

All commands in this readme get run from the ``service`` directory.


Installation
------------

After the [initial Python/machine installation](../README.md#installation) 
and following the [getting started with the services guide](../README.md#getting-started)
you can further setup your Django database for the API with the following commands.

```bash
export DJANGO_POSTGRES_USER=postgres  # the root user who will own all tables
python manage.py migrate
```

This should have setup your database for the most part.
Unfortunately due to historic reasons there is a lot of configuration going on in the database.
So it's wise to get a production dump and import it to your system.
Please ask somebody access to the S3 database dumps bucket.
Place the latest dump inside ``postgres/dumps`` and then run:

```bash
make import-db backup=postgres/dumps/<dump-file-name>.sql
```

To finish the setup you can create a superuser for yourself using the ``createsuperuser`` command
from the ``service`` directory.

```bash
python manage.py createsuperuser
```


Getting started
---------------

There are three ways to get the ``service`` component started.
You can either start all services as explained in the [general getting started guide](../README.md#getting-started).
Or you can start a local development server with:

```bash
make run-django
```

The last option is to start a container outside of docker-compose orchestration.
This makes it easier to connect a debugger to it.
Start a container with a UWSGI production server with:

```bash
make run-service-container
```


#### Available apps

Either way the Django admin and API endpoints become available under:

```bash
http://localhost:8000/admin/
http://localhost:8000/api/v1/
```


#### Production parity on localhost

If you want to test the app with highest possible parity with production,
then you need to run the following

```bash
cd ..
APPLICATION_MODE=development docker-compose up
```

Then you can visit the frontend through

```bash
http://localhost:8000/
```

This will serve the frontend and backend through (a multi process) UWSGI server.
It will also try to access AWS services in the ``surfpol-dev`` account.
This is very similar to how it works on AWS and in production.
A major difference is the load balancer in front of UWSGI, which is missing in the local setup.


#### Migrate locally

Database tables are owned by the root database user called "postgres".
This is a different user than the application database user.
and that causes problems when you try to migrate,
because the application user is not allowed to alter or create anything.

To apply migrations locally you'll need to switch the connection to the root user.
You can do so by setting an environment variable before running the migration:

```bash
export DJANGO_POSTGRES_USER=postgres
python manage.py migrate
```


Tests
-----

The test suite is rather limited at the moment. There's not real tests at all for the portal.
However there are some tests for the integration with
the Edurep search engine and our own Elastic Search powered engine.
These engines are what makes the portal tick in the end
and currently you can switch between the two engines with a deploy.
The adapter that connects to these search engines is fully tested.
These tests also assert that the two engines return more or less the same content.
This is to keep the ability to switch engines when needed.

Run these integration tests with the following command:

```bash
make integration-tests
```


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
invoke srv.setup
```

This should have setup your database for the most part.
Unfortunately due to historic reasons there is a lot of configuration going on in the database.
So it's wise to get a production dump and import it to your system.
You can do this with:

```bash
invoke db.import-snapshot
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
export POL_DJANGO_POSTGRES_USER=postgres
python manage.py migrate
```


Tests
-----

In order to test your work in combination with harvester code as well as frontend code.
It's recommended to [run your tests from the repo root](../README.md#tests).

To only test the service you can run standard Django tests and specify submodules.
For example:

```bash
python manage.py test surf.apps
```

To do e2e testing for this project and the portal frontend you can run:

```bash
cd ..
invoke e2e_tests
```


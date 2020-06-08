Search Portal
=============

Search service for finding open access higher education learning materials.

The repo consists of a frontend, a backend and a background task component.
The frontend is called ``portal`` and is a Vue SPA.
The backend is named ``service``, which is mostly a REST API, but also serves the frontend SPA and Django admin pages.
Background tasks are handled by a Celery Django app named ``harvester``,
but there is also an admin available for that part.


Prerequisites
-------------

This project uses ``Python 3.6``, ``npm``, ``Docker`` and ``docker-compose``.
Make sure they are installed on your system before installing the project.


Installation
------------

The local setup is made in such a way that you can run the project inside and outside of containers.
It can be convenient to run some code for inspection outside of containers.
To stay close to the production environment it works well to run the project in containers.
External services like the database run in containers so it's always necessary to use Docker.


#### General setup

To install the basic environment and tooling you'll need to first setup a local environment on a host machine with:

```bash
python3 -m venv venv
source activate.sh
pip install --upgrade pip
pip install -r requirements.txt
```

Then copy the ``.env.example`` file to ``.env`` and update the variable values to fit your system.
You'll at least need to provide your Elastic Search credentials and AWS credentials.

If you want to run the project outside of a container you'll also need to add ``POL_DJANGO_POSTGRES_HOST=127.0.0.1``
to the ``.env`` file or add ``127.0.0.1 postgres`` to your hosts file, in order for the service to pickup the database.
Similarly for the Elastic cluster you need to add ``POL_ELASTIC_SEARCH_HOST=127.0.0.1`` to the ``.env`` file
or add ``127.0.0.1 elasticsearch`` to your hosts file.

To finish the general setup you can run this command to build all containers:

```bash
docker-compose -f docker-compose.yml up --build
```


##### Elastic Search setup

It's possible to load data into the Elastic Search cluster from a few commands
In order to do that you first need to setup with:

```bash
invoke es.setup
```

Backups are stored in a so called repository. You'll need to download the latest ES repository file to load the data.
Ask somebody for the file and name of the latest backup repository and run:

```bash
invoke es.load-repository <repository-file>
invoke es.restore-snapshot <repository-name>
```

This should have loaded the indices you need to make searches locally.
Alternatively you can set the
``POL_ELASTIC_SEARCH_HOST``, ``POL_ELASTIC_SEARCH_PROTOCOL``, ``POL_ELASTIC_SEARCH_USERNAME`` and
``POL_SECRETS_ELASTIC_SEARCH_PASSWORD`` variables inside your ``.env`` file.
This allows to connect your local setup to a remote development or testing cluster.


#### Resetting your database

Sometimes you want to start fresh.
If your database container is not running it's quite easy to throw all data away and create the database from scratch.
To irreversibly destroy your local database with all data run:

```bash
docker volume rm search-portal_postgres_database
```

And then follow the steps above to recreate the database and populate it.


Getting started
---------------

The local setup is made in such a way that you can run the components of the project inside and outside of containers.
External services like the database always run in containers.
Make sure that you're using a terminal that you won't be using for anything else, 
as any containers will print their output to the terminal.
Similar to how the Django developer server prints to the terminal.

> When any containers run you can halt them with ``CTRL+C``.
> To completely stop containers and release resources you'll need to run "stop" or "down" commands.
> As explained below.

With any setup it's always required to use the activate.sh script to **load your environment**.
This takes care of important things like local CORS and database credentials.

```bash
source activate.sh
```

When you've loaded your environment you can choose to only start/stop the database and ES node by using:

```bash
make start-services
make stop-services
```

After that you can follow the guides to [start the service](service/README.md),
[work with the frontend](portal/README.md) or start the harvester.
Alternatively you can choose to run all components of the project in containers with:

```bash
docker-compose up
docker-compose down
```


#### Available apps

Either way the database admin tool become available under:

```bash
http://localhost:8081/
```


Tests
-----

You can run all tests for the entire project by running:

```bash
invoke test
```

Often you'll only want to test part of the project like ``service`` or ``harvester``.
You can specify a target to the test command to run parts of the test suite.
To only run the Selenium integration tests for example you can run:

```bash
invoke test --target service~surf.apps
```

For the complete list of possible targets run:

```bash
invoke -h test
```

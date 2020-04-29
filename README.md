Search Portal
=============

A search service for finding open access higher education learning materials.

The repo consists of a frontend and a backend. The frontend is called ``portal`` and is a Vue SPA. 
The backend is named ``service``, which is mostly a REST API, but also serves the frontend SPA and Django admin pages.


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

#### Backend


To install the backend you'll need to first setup a local environment on a host machine with:

```bash
python3 -m venv venv
source activate.sh
pip install --upgrade pip
pip install -r service/requirements.txt
```

Then copy the ``.env.example`` file to ``.env`` and update the variable values to fit your system.
You'll at least need to provide your Elastic Search credentials and AWS credentials.

If you want to run the project outside of a container you'll also need to add ``DJANGO_POSTGRES_HOST=127.0.0.1``
to the ``.env`` file or add ``127.0.0.1 postgres`` to your hosts file, in order for the service to pickup the database.

After this you can setup your database with the following commands:

```bash
docker-compose -f docker-compose.yml up --build
source activate.sh  # perhaps redundant, already activated above
export DJANGO_POSTGRES_USER=postgres  # the root user who will own all tables
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

The local setup is made in such a way that you can run the project inside and outside of containers.
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

When you've loaded your environment you can choose to only start/stop the database using:

```bash
make start-db
make stop-db
```

After that you can start your local Django development server in the ``service`` directory.

Or you can choose to run the entire project in containers with:

```bash
docker-compose up
docker-compose down
```

Either way the Django admin, API and a database admin tool become available under:

```bash
http://localhost:8000/admin/
http://localhost:8000/api/v1/
http://localhost:8081/  # for database administration
```

Last but not least you'll have to start the Vue frontend with:

```bash
cd portal
npm run serve
```

Which makes the frontend available through:

```bash
http://localhost:8080/
```


#### Logging in locally

On the servers the login works through SURFConext.
It's a bit of a hassle to make that work locally.
So we've opted for a way to work around SURFConext when logging in during development.

Simply login to the Django admin.
Once logged in clicking the frontend login button.
This will fetch an API token on Vue servers in development mode and "log you in".
From there on out there is no difference between the remote and local login.


#### Migrate locally

Database tables are owned by the root database user called "postgres".
This is a different user than the application database user.
and that causes problems when you try to migrate,
because the application user is not allowed to alter or create anything.

To apply migrations locally you'll need to switch the connection to the root user.
You can do so by setting an environment variable before running the migration:

```bash
export DJANGO_POSTGRES_USER=postgres
cd service
python manage.py migrate
```

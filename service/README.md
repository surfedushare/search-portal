# Search Portal Service

A REST API build with Django and Django Rest Framework.
There is an admin available to inspect the data.

All commands in this readme get run from the `service` directory.

## Installation

After the [initial Python/machine installation](../README.md#installation)
and following the [getting started guide](../README.md#getting-started)
you can further setup your Django database for the API with the following commands.

```bash
invoke srv.setup-postgres
```

This should have setup your database completely.
However it can be beneficial to get a production dump and import it to your system.

Make sure you are connected to eduvpn and in the root of this repo.

You can create such a dump with:

```
APPLICATION_MODE=production fab -H bastion.prod.surfedushare.nl srv.create-snapshot
```

The output of this command will include a SQL file name. You can then use that name to import the dump locally:

```bash
invoke srv.import-snapshot -s pol-prod
(uses the last snapshot)

or

invoke srv.import-snapshot -s pol-dev -n <sql-file-name>
(uses a specific snapshot)
```

To create Open Search indices with test materials you can execute the following:

```
invoke srv.recreate-test-indices
```

## Getting started

There are three ways to get the `service` component started.
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

#### Using Opensearch from acceptance

It's possible to connect to the Opensearch instance in the AWS acceptance environment.
This can be useful to test locally with real data to solve bugs.
In order to do this you need to add the following to your ``.env`` file

```
POL_OPENSEARCH_HOST=https://search-surfpol-main-lg7ozt5vp3oamyuiykxbghsthq.eu-central-1.es.amazonaws.com
POL_OPENSEARCH_ALIAS_PREFIX=edusources
POL_SECRETS_OPENSEARCH_PASSWORD=<password>
```

Where <password> should get replaced with the password of the acceptance Opensearch superuser.
After this you should re-start containers in order to load these variables.
If you're working in a shell you should also run ``source activate.sh`` again to load the variables.

If you want to disconnect from the acceptance instance
you can set all the variables above to nothing like in ``.env.example``.
Once you restart the docker containers and reload variables in shells
everything should be connected to your local Opensearch again.

#### Available apps

Either way the Django admin and API endpoints become available under:

```bash
http://localhost:8000/admin/
http://localhost:8000/api/v1/
```

The setup command will have created a superuser called supersurf. On localhost the password is "qwerty".
For AWS environments you can find the admin password under the Django secrets in the Secret Manager.

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
It will also try to access AWS services in the `surfpol-dev` account.
This is very similar to how it works on AWS and in production.
A major difference is the load balancer in front of UWSGI, which is missing in the local setup.

#### Translations

There are very few Django translations as yet.
Keep in mind that the default language is NL and that translatable strings in code should be Dutch.
To gather all translations and aggregate them into a file run:

```
invoke srv.make-translations
```

## Tests

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
invoke test.e2e
```

## Provisioning

The service only needs to provision its database. To setup the database on an AWS environment run:

> If you setup the database in this way all data is irreversibly destroyed

```bash
APPLICATION_MODE=<environment> fab -H <bastion-host-domain> srv.setup-postgres
```

To load snapshot data into the database on an AWS environment run:

```bash
APPLICATION_MODE=<environment> fab -H <bastion-host-domain> srv.restore-snapshot -s pol-dev <sql-file-name>
```

The SQL file name is the file name as printed by [the create snapshot](README.md#installation) command described above

# Deploy

For manual deployment of the service project take the following steps

- invoke aws.build service
- invoke aws.push service --docker-login
- APPLICATION_MODE=acceptance invoke aws.promote service
- APPLICATION_MODE=acceptance invoke srv.deploy acceptance

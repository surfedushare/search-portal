Harvester
=========

A Django project made to run long-running tasks.
It will connect over OAI-PMH to different repositories and index learning materials from these repositories
in an Elastic Search instance.


Installation
------------

After the [initial Python/machine installation](../README.md#installation)
and following the [getting started guide](../README.md#getting-started)
you can further setup your Django database for the harvester with the following commands.

```bash
invoke hrv.setup-postgres
```

Last but not least you'll need to add this to your hosts file to make Redis work outside of containers:

```
127.0.0.1       redis
```


Getting started
---------------

There are two ways to get the ``harvester`` component started.
You can either start all services as explained in the [general getting started guide](../README.md#getting-started).
Or you can start services manually with the following commands:

##### The Django development server for the admin

```bash
make run-django
```

This makes the admin available at:

```
http://localhost:8888/admin/
```

The setup command will have created a superuser called supersurf. On localhost the password is "qwerty".
For AWS environments you can find the admin password under the Django secrets in the Secret Manager.


##### A Celery development worker for processing background tasks

```
celery -A harvester worker -l info
```

##### [optional] A Django shell to call background tasks synchronously

```
python manage.py shell
```

##### [optional] A Flow-er service that monitors background tasks

```
flower -A harvester
```


Harvesting
----------

Harvesting is fairly straightforward. You need at least one 'active' ``Dataset``.
The test ``Dataset`` is active by default.
You can activate a ``Dataset`` through the Django admin under the ``core`` app.
Once harvested all materials belonging to a ``Dataset`` will be fully processed
and available in your Elastic Search indices.

You can run the following command to harvest content and update all active ``Datasets`` at once:

```
invoke hrv.harvest localhost
```

Or when dealing with AWS remotes:

```
APPLICATION_MODE=<mode> invoke hrv.harvest <mode>
```

#### What a harvest actually does

A harvest undertakes the following steps:

* Gather metadata from a repository (at the moment that's only Edurep)
* Download all files to S3 if they haven't been downloaded before
* Extract content from the files with Tika
* Merge metadata and content into a ``Document`` of the ``Dataset``. A URL is represented with an ``Arrangement``
* Upsert all ``Arrangements`` of the ``Dataset`` to Elastic Search and remove deleted ``Arrangements``


#### How to add more materials to a Dataset

In the admin you can see that a ``Dataset`` contains a number of ``Sources``.
By adding or removing a source you add or remove materials from those ``Sources``.
A source needs a ``spec`` which refers to the ``setSpec`` definition in the
[OAI-PMH protocol](http://www.openarchives.org/OAI/openarchivesprotocol.html#Set).
Make sure that value matches a ``setSpec`` that exists inside the repository you want to target.


Harvesting on AWS
-----------------

As explained before in the harvesting section you'll need to run the following to harvest for a particular environment:

```
APPLICATION_MODE=<mode> invoke hrv.harvest <mode>
```

Where mode can be one of: localhost, development, acceptance or production.

Seeing the results on AWS can be done by port-forwarding the relevant services in the cluster.
There are convenience commands to do this. For example to connect to the development UWSGI server use:

```
APPLICATION_MODE=development fab -H bastion.dev.surfedushare.nl hrv.connect-uwsgi development
```

To see the Flower you can run:

```
APPLICATION_MODE=development fab -H bastion.dev.surfedushare.nl hrv.connect-uwsgi development
```


Tests
-----

In order to test your work in combination with search service code as well as frontend code.
It's recommended to [run your tests from the repo root](../README.md#tests).

To only test the harvester you can run standard Django tests:

```bash
python manage.py test
```


Provisioning
------------

The service only needs to provision the database and Elastic Search.
To setup the database on an AWS environment run:

> If you setup the database in this way all data is irreversibly destroyed

```bash
APPLICATION_MODE=<environment> fab -H <bastion-host-domain> hrv.setup-postgres
```

To load the latest production data into the database and push that data to Elastic Search on an AWS environment run:

```bash
APPLICATION_MODE=<environment> invoke import-dataset <environment> -s production -d <dataset-name>
```

To load data for localhost you have to use a slightly different command,
because your profile will need access to the source.

```bash
AWS_PROFILE=pol-prod invoke import-dataset localhost -s production -d <dataset-name>
```

The harvester keeps its harvest results in the database. It may be required to clean these results to start fresh.
You can force deletion of previous results with:

```bash
APPLICATION_MODE=<environment> invoke hrv.cleanup <environment>
```

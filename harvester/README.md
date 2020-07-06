Harvester
=========

A Django project made to run long-running tasks.
It will connect over OAI-PMH to different repositories and index learning materials from these repositories
in an Elastic Search instance.


Installation
------------

After the [initial Python/machine installation](../README.md#installation)
and following the [getting started with the services guide](../README.md#getting-started)
you can further setup your Django database for the harvester with the following commands.

```bash
invoke hrv.setup
```

#### Installing a dataset

You can install a local dataset with the following command:

```bash
invoke hrv.import-dataset
```


Tests
-----

In order to test your work in combination with search service code as well as frontend code.
It's recommended to [run your tests from the repo root](../README.md#tests).

To only test the harvester you can run standard Django tests:

```bash
python manage.py test
```

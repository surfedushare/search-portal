Harvester
=========

A Django project made to run long-running tasks.
It will connect over OAI-PMH to different repositories and index learning materials from these repositories
in an Elastic Search instance.


Tests
-----

In order to test your work in combination with search service code as well as frontend code.
It's recommended to [run your tests from the repo root](../README.md#tests).

To only test the harvester you can run standard Django tests:

```bash
python manage.py test
```

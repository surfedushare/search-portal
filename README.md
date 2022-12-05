# Search Portal

Search service for finding open access higher education learning materials.

The repo consists of a frontend, a backend and a background task component.
The frontend is called `portal` and is a Vue SPA.
The backend is named `service`, which is mostly a REST API, but also serves the frontend SPA and Django admin pages.
Background tasks are handled by a Celery Django app named `harvester`,
but there is also an admin available for that part.

## Prerequisites

This project uses `Python 3.10`, `npm`, `Docker`, `docker-compose` and `psql`.
Make sure they are installed on your system before installing the project.

## Installation

The local setup is made in such a way that you can run the project inside and outside of containers.
It can be convenient to run some code for inspection outside of containers.
To stay close to the production environment it works well to run the project in containers.
External services like the database run in containers, so it's always necessary to use Docker.

#### Mac OS setup

We recommend installing Python through pyenv:

```
brew update && brew upgrade pyenv
pyenv install 3.10.4
```

When using macOS make sure you have `libmagic` installed. It can be installed using `brew install libmagic`.

#### General setup

To install the basic environment and tooling you'll need to first setup a local environment on a host machine with:

```bash
python3 -m venv venv --copies --upgrade-deps
source activate.sh
pip install setuptools==58
pip install -r requirements.txt
```

Then copy the `.env.example` file to `.env` and update the variable values to fit your system.
For a start the default values will do.

When using vscode copy `activate.sh` to venv/bin so pylance can find it.

If you want to run the project outside of a container you'll need to add the following to your hosts file:

```
127.0.0.1 postgres
127.0.0.1 opensearch
127.0.0.1 harvester
127.0.0.1 service
```

This way you can reach these containers outside of the container network through their names.
This is important for many setup commands as well as the integration tests and running the service locally.

To finish the general setup you can run these commands to build all containers:

```bash
invoke aws.sync-repository-state
invoke prepare-builds
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 017973353230.dkr.ecr.eu-central-1.amazonaws.com
docker-compose -f docker-compose.yml up --build
```

## Getting started

The local setup is made in such a way that you can run the components of the project inside and outside of containers.
External services like the database always run in containers.
Make sure that you're using a terminal that you won't be using for anything else,
as any containers will print their output to the terminal.
Similar to how the Django developer server prints to the terminal.

> When any containers run you can halt them with `CTRL+C`.
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
[work with the frontend](portal/README.md) or [start the harvester](harvester/README.md).
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

#### Resetting your database

Sometimes you want to start fresh.
If your database container is not running it's quite easy to throw all data away and create the database from scratch.
To irreversibly destroy your local database with all data run:

```bash
docker volume rm search-portal_postgres_database
```

And then follow the steps to [install the service](service/README.md#installation) and
[install the harvester](harvester/README.md#installation) to recreate the databases and populate them.

## Tests

You can run all tests for the entire repo by running:

```bash
invoke test.run
```

It's also possible to run tests for specific Django services.
For more details see: [testing service](service/README.md#tests) and
[testing harvester](harvester/README.md#tests)

## Deploy

This section outlines the most common options for deployment.
Use `invoke -h <command>` to learn more about any invoke command.

The pipelines on gitlab use a [gitlab runner image](Dockerfile-runner) where all requirements are pre-installed, if you update a dependency you should run `invoke aws.publish-runner-image --docker-login`

Before deploying you'll want to decide on a version number.
It's best to talk to the team about which version number you want to use for a deploy.
To see a list of all currently available images for a project and the versions they are tagged with you can run
the following command.
Where `<target-project-name>` will be `harvester` or `service`.

```bash
invoke aws.print-available-images <target-project-name>
```

Make sure that the version inside of `harvester/package.py` and `service/package.py`
is different from any other version in the AWS image registries (both service and harvester registry).
Commit a version change if this is not the case.
Then push to do the Gitlab remote and wait until the pipeline completes.
The final pipeline job is manual.
It will tag the image the pipeline has build with the version number from the package files if you run it.

When an image is build with the pipeline and tagged with the version you can deploy the service with:

```bash
APPLICATION_MODE=<environment> invoke srv.deploy <environment>
```

And the harvester with:

```bash
APPLICATION_MODE=<environment> invoke hrv.deploy <environment>
```

These last deploy commands will wait until all containers in the AWS cluster have been switched to the new version.
This may take some time and the command will indicate that it is waiting to complete.
If you do not want to wait you can `CTRL+C` in the terminal safely. This cancels the waiting, not the deploy itself.

Also note that these commands will deploy the image with a version tag to whatever is in your package.py files.
If you want to deploy a different version use the `--version` flag with the commands above.

#### Release

A special case of deploying is releasing. You should take the following steps during releasing:

- Create a PR from `acceptance` to the `edusources` or `nppo` branch (depending on which project you want to release)
- There are a few things that you should check in a release PR, because it influences the release steps:
  - Are there any database migrations?
  - Are there changes to Open Search indices?
  - Is it changing the public harvester API that the search service is consuming?
  - Is it depending on infrastructure changes?
- Plan your release according to the questions above.
  Use common sense for this and take into account that we do rolling updates.
  For example if you're deleting stuff from the database, indices, API or infratructure,
  then code that stops using the stuff should be deployed before the actual deletions take place.
  If you're adding to the database, indices, API or infrastructure then they should get added
  before code runs that expect these additions.
  We write down these steps, together with their associated commands if applicable, in Pivotal tickets to remember them.
- With complicated changes we prefer to try them on development
  and we create the release plan when putting the changes on acceptance.
  When we release to production following the plan should be sufficient to make a smooth release.
- When dealing with breaking changes we make a release tag on the `edusources` branch.
  The tag is equal to the release version prefixed with a "v" so for instance: v0.0.1
  This allows us to easily jump back to a version without these breaking changes through git.
- Once the release plan is executed on production and a tag for the previous release is created when necessary then
  we merge the release PR into its branch.
- After de pipeline has finished, run
  APPLICATION_MODE=production invoke srv.deploy production
  APPLICATION_MODE=production invoke hrv.deploy production
- check https://edusources.nl/health/ for the right version
- check https://harvester.prod.surfedushare.nl/ for the right version

This completes the release, which we mark in Pivotal by "finishing" the release ticket.
We also post a message into Teams if people are waiting for certain features.

As you can see the release may consist of many steps and release plans can become elaborate.
Here is an overview of commands that are regularly used during a release and their relevant documentation:

- [Database migration](#Migrate)

- [Harvesting](harvester/README.md#Harvesting on AWS)
- Index recreation. See: `invoke -h hrv.index-dataset-version`
  (this doesn't collect documents from sources like harvesting, but does recreate indices for a Dataset)
- [Terraform](https://www.terraform.io/intro)

#### Active containers/versions

You can see which containers and which versions of a project are currently active for a particular environment by using:

```bash
APPLICATION_MODE=<environment> invoke aws.print-running-containers <target-project-name> <environment>
```

#### Rollback

In order to rollback you can specify an existing Docker image to deploy command.
For instance with the service:

```bash
APPLICATION_MODE=<environment> invoke srv.deploy <environment> -v <rollback-version>
```

#### Migrate

To migrate the database on AWS you can run the migration command:

```bash
APPLICATION_MODE=<environment> invoke aws.migrate <target-project-name> <environment>
```

## Provisioning

There are a few commands that can help to provision things like the database on AWS.
We're using Fabric for provisioning.
You can run `fab -h <command>` to learn more about a particular Fabric command.

For more details on how to provision things on AWS see [provisioning the service](service/README.md#provisioning) and
[provisioning the harvester](harvester/README.md#provisioning)

## Linting

The python code uses flake8 as a linter. You can run it with the following command:

```bash
flake8 .
```

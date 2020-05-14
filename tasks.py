import os
import json

from invoke import Collection
from invoke.tasks import task
from git import Repo

from environments.configuration import environment
from environments.package import get_package_info
from elastic.tasks import setup, create_snapshot, load_repository, restore_snapshot

from service.package import VERSION as SERVICE_VERSION


@task()
def prepare_builds(ctx):
    repo = Repo(".")
    commit = str(repo.head.commit)
    with open(os.path.join("portal", "package.json")) as portal_package_file:
        portal_package = json.load(portal_package_file)
    info = {
        "commit": commit,
        "versions": {
            "service": SERVICE_VERSION,
            "portal": portal_package["version"]
        }
    }
    with open(os.path.join("environments", "info.json"), "w") as info_file:
        json.dump(info, info_file)


@task(prepare_builds)
def build_service(ctx):
    package_info = get_package_info()
    commit = package_info["commit"]
    version = package_info["versions"]["service"]
    ctx.run(f"docker build -t search-portal:{version} -t search-portal:{commit} .", pty=True, echo=True)

namespace = Collection(
    Collection("es", setup, create_snapshot, load_repository, restore_snapshot),
    prepare_builds,
    build_service
)
namespace.configure(environment)

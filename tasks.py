from invoke import Collection

from environments.surfpol import environment
from elastic.tasks import setup, create_snapshot, load_repository, restore_snapshot
from deploy import prepare_builds, build, push, deploy
from test import test


namespace = Collection(
    Collection("es", setup, create_snapshot, load_repository, restore_snapshot),
    prepare_builds,
    build,
    push,
    deploy,
    test
)
namespace.configure(environment)

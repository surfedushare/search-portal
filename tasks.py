from invoke import Collection

from environments.configuration import environment
from elastic.tasks import setup, create_snapshot, load_repository, restore_snapshot


namespace = Collection(
    Collection("es", setup, create_snapshot, load_repository, restore_snapshot)
)
namespace.configure(environment)

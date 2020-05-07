from invoke import Collection

from environments.configuration import environment
from elastic.tasks import setup


namespace = Collection(
    Collection("es", setup)
)
namespace.configure(environment)

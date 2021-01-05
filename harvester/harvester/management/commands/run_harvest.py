from harvester.background import harvest
from core.management.base import HarvesterCommand


class Command(HarvesterCommand):
    """
    A command that calls the harvest background task.
    Normally this background task runs once a day, but we may want to trigger this manually as well,
    especially during development on AWS
    """

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-r', '--reset', action="store_true",
                            help="Resets the Dataset model to be empty and deletes all OAI-PMH data")
        parser.add_argument('-s', '--source', type=str,
                            help="Indicates to run the harvest as replication of a source")

    def handle(self, **options):
        reset = options["reset"]
        source = options.get("source", None)
        self.info(f"Calling harvest outside of schedule; reset={reset}")
        harvest(seeds_source=source, reset=reset)

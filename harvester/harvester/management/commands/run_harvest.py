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
        parser.add_argument('-s', '--secondary', action="store_true",
                            help="Indicates to run the harvest on a secondary (replication) node")

    def handle(self, **options):
        reset = options["reset"]
        role = "secondary" if options["secondary"] else "primary"
        self.info(f"Calling harvest outside of schedule; reset={reset}")
        harvest(role=role, reset=reset)

import logging

from django.core.management import base, call_command


logger = logging.getLogger("harvester")


class Command(base.LabelCommand):
    """
    A convenience command that calls the load_harvester_data and push_es_index commands together.
    This will get the harvest data from the specified source (or the current environment),
    load the data into the database and then perform an Elastic Search update.
    """

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-s', '--skip-download', action="store_true")
        parser.add_argument('-hs', '--harvest-source', type=str)

    def handle_label(self, dataset, **options):
        harvest_source = options.get("harvest_source", None)
        logger.info(f"Calling import_dataset for: {dataset} using:{harvest_source}")
        extra_args = [] if harvest_source is None else [f"--harvest-source={harvest_source}"]
        call_command("load_harvester_data", dataset, *extra_args)
        call_command("push_es_index", dataset=dataset, recreate=True)

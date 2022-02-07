import logging

from django.db.transaction import atomic

from core.models import Harvest


logger = logging.getLogger("harvester")


@atomic()
def prepare_harvest(dataset, reset=False):

    excluded_specs = []
    for harvest in Harvest.objects.filter(dataset=dataset).select_for_update():
        if reset or harvest.should_purge():
            logger.debug(f"Resetting harvest stage for '{harvest.source.name}'")
            harvest.reset()
            logger.info(f"Clearing resources for '{harvest.source.name}'")
            harvest.source.clear_repository_resources()
            excluded_specs.append(harvest.source.spec)
        else:
            logger.debug(f"Setting harvest stage to NEW for '{harvest.source.name}'")
            harvest.prepare()

    dataset.create_new_version(excluded_specs=excluded_specs)

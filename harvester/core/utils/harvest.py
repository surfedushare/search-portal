import logging

from django.db.models import Count
from django.db.transaction import atomic

from core.models import Harvest, Batch, ProcessResult


logger = logging.getLogger("harvester")


@atomic()
def prepare_harvest(dataset, reset=False):

    excluded_specs = []
    for harvest in Harvest.objects.filter(dataset=dataset).select_for_update():
        logger.info(f"Clearing resources for '{harvest.source.name}'")

        if reset or harvest.should_purge():
            logger.debug(f"Resetting harvest stage for '{harvest.source.name}'")
            harvest.reset()
            harvest.source.clear_repository_resources()
            excluded_specs.append(harvest.source.spec)
        else:
            logger.debug(f"Setting harvest stage to NEW for '{harvest.source.name}'")
            harvest.prepare()
            harvest.source.mark_repository_resources_as_extracted()

    dataset.create_new_version(excluded_specs=excluded_specs)

    # Check if there are any process_result leftovers from a previous harvest process
    logged_result_types = set()
    for process_result in ProcessResult.objects.all():
        if process_result.result_type not in logged_result_types:
            logger.warning(f"Found unexpected process results for result type: {process_result.result_type}")
            logged_result_types.add(process_result.result_type)
    # Delete all batches that have been processed fully
    Batch.objects.annotate(doc_count=Count("documents")).filter(doc_count=0).delete()

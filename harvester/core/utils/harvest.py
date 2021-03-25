import logging

from core.models import Arrangement, Harvest
from core.constants import HarvestStages


logger = logging.getLogger("harvester")


def prepare_harvest(dataset):
    logger.debug("Deleting arrangements in trash")
    Arrangement.objects.filter(deleted_at__isnull=False).delete()
    harvest_queryset = Harvest.objects.filter(
        dataset=dataset,
        stage=HarvestStages.COMPLETE
    )
    for harvest in harvest_queryset:
        logger.debug(f"Setting harvest stage to NEW for '{harvest.source.name}'")
        harvest.stage = HarvestStages.NEW
        harvest.latest_update_at = harvest.harvested_at
        harvest.save()

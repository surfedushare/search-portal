import logging

from core.models import Harvest
from core.constants import HarvestStages


logger = logging.getLogger("harvester")


def prepare_harvest(dataset):
    harvest_queryset = Harvest.objects.filter(
        dataset=dataset,
        stage=HarvestStages.COMPLETE
    )
    for harvest in harvest_queryset:
        logger.debug(f"Setting harvest stage to NEW for '{harvest.source.name}'")
        harvest.stage = HarvestStages.NEW
        harvest.latest_update_at = harvest.harvested_at
        harvest.save()

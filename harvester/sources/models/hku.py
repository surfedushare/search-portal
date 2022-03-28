import logging

from django.conf import settings
from django.db import models

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from core.models import HarvestHttpResource
from sources.extraction.hku import HkuMetadataExtraction, HKU_EXTRACTION_OBJECTIVE


logger = logging.getLogger("harvester")


class HkuMetadataResourceManager(models.Manager):

    def extract_seeds(self, latest_update):
        queryset = self.get_queryset() \
            .filter(since__date__gte=latest_update.date(), status=200)

        metadata_objective = {
            "@": "$.root.item",
            "external_id": "$.resultId",
            "state": HkuMetadataExtraction.get_record_state
        }
        metadata_objective.update(HKU_EXTRACTION_OBJECTIVE)
        extract_config = create_config("extract_processor", {
            "objective": metadata_objective
        })
        prc = ExtractProcessor(config=extract_config)

        results = []
        for harvest in queryset:
            seed_resource = {
                "resource": f"{harvest._meta.app_label}.{harvest._meta.model_name}",
                "id": harvest.id,
                "success": True
            }
            for seed in prc.extract_from_resource(harvest):
                seed["seed_resource"] = seed_resource
                results.append(seed)
        return results


class HkuMetadataResource(HarvestHttpResource):

    objects = HkuMetadataResourceManager()

    set_specification = models.CharField(max_length=255, blank=True, null=False, default="hku")
    use_multiple_sets = False

    URI_TEMPLATE = settings.SOURCES["hku"]["endpoint"] + "/octo/repository/api2/getResults" \
        if settings.SOURCES["hku"]["endpoint"] else "/octo/repository/api2/getResults"

    PARAMETERS = {
        "format": "json",
        "project": "pubplatv4"
    }

    class Meta:
        verbose_name = "HKU metadata harvest"
        verbose_name_plural = "HKU metadata harvests"

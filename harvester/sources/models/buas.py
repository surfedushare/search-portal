import logging

from django.conf import settings
from django.db import models

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from core.models import HarvestHttpResource
from sources.extraction.buas import BuasMetadataExtraction


logger = logging.getLogger("harvester")


class BuasPureResourceManager(models.Manager):

    def extract_seeds(self, latest_update):
        queryset = self.get_queryset() \
            .filter(since__date__gte=latest_update.date(), status=200)

        metadata_objective = {
            "@": "$.items",
            "external_id": "$.uuid",
            "state": BuasMetadataExtraction.get_record_state
        }
        metadata_objective.update(BuasMetadataExtraction.OBJECTIVE)
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


class BuasPureResource(HarvestHttpResource):

    objects = BuasPureResourceManager()

    set_specification = models.CharField(max_length=255, blank=True, null=False, default="buas")
    use_multiple_sets = False

    URI_TEMPLATE = settings.SOURCES["buas"]["endpoint"] + "/ws/api/523/research-outputs" \
        if settings.SOURCES["buas"]["endpoint"] else "/ws/api/523/research-outputs"

    HEADERS = {
        "accept": "application/json"
    }

    def auth_headers(self):
        return {
            "api-key": settings.SOURCES["buas"]["api_key"]
        }

    def next_parameters(self):
        content_type, data = self.content
        count = data["count"]
        page_info = data["pageInformation"]
        offset = page_info["offset"]
        size = page_info["size"]
        remaining = count - (offset + size)
        if remaining <= 0:
            return {}
        return {
            "size": size,
            "offset": offset + size
        }

    class Meta:
        verbose_name = "BUAS Pure harvest"
        verbose_name_plural = "BUAS Pure harvests"

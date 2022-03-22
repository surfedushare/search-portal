import logging

from django.conf import settings
from django.db import models

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from core.models import HarvestHttpResource
from sources.extraction.hva import HvaMetadataExtraction, HVA_EXTRACTION_OBJECTIVE


logger = logging.getLogger("harvester")


class HvaPureResourceManager(models.Manager):

    def extract_seeds(self, latest_update):
        queryset = self.get_queryset() \
            .filter(since__date__gte=latest_update.date(), status=200)

        metadata_objective = {
            "@": "$.items",
            "external_id": "$.uuid",
            "state": HvaMetadataExtraction.get_record_state
        }
        metadata_objective.update(HVA_EXTRACTION_OBJECTIVE)
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


class HvaPureResource(HarvestHttpResource):

    objects = HvaPureResourceManager()

    set_specification = models.CharField(max_length=255, blank=True, null=False, default="hva")
    use_multiple_sets = False

    URI_TEMPLATE = settings.SOURCES["hva"]["endpoint"] + "/ws/api/research-outputs" \
        if settings.SOURCES["hva"]["endpoint"] else "/ws/api/research-outputs"

    def auth_headers(self):
        return {
            "api-key": settings.SOURCES["hva"]["api_key"]
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
        verbose_name = "HAN OAIPMH harvest"
        verbose_name_plural = "HAN OAIPMH harvests"

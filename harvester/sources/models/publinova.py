import logging
from urlobject import URLObject

from django.conf import settings
from django.db import models

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor

from core.models import HarvestHttpResource
from sources.extraction.publinova import PublinovaMetadataExtraction, PUBLINOVA_EXTRACTION_OBJECTIVE


logger = logging.getLogger("harvester")


class PublinovaMetadataResourceManager(models.Manager):

    def extract_seeds(self, latest_update):
        queryset = self.get_queryset().filter(
            since__date__gte=latest_update.date(),
            status=200,
            is_extracted=False
        )

        metadata_objective = {
            "@": "$.data",
            "external_id": "$.id",
            "state": PublinovaMetadataExtraction.get_record_state
        }
        metadata_objective.update(PUBLINOVA_EXTRACTION_OBJECTIVE)
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


class PublinovaMetadataResource(HarvestHttpResource):

    objects = PublinovaMetadataResourceManager()

    set_specification = models.CharField(max_length=255, blank=True, null=False, default="publinova")
    use_multiple_sets = False

    URI_TEMPLATE = settings.SOURCES["publinova"]["endpoint"] + "/sources/products" \
        if settings.SOURCES["publinova"]["endpoint"] else "/sources/products"

    def auth_headers(self):
        return {
            "Authorization": f"Bearer {settings.SOURCES['publinova']['api_key']}"
        }

    def next_parameters(self):
        content_type, data = self.content
        next_link = data["links"].get("next", None)
        if not next_link:
            return {}
        next_url = URLObject(next_link)
        return {
            "page": next_url.query_dict["page"]
        }

    class Meta:
        verbose_name = "Publinova harvest"
        verbose_name_plural = "Publinova harvests"

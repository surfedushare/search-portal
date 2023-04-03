from django.db import models

from datagrowth.configuration import create_config
from datagrowth.processors import ExtractProcessor
from core.models import HarvestHttpResource
from sources.extraction.edurep import EdurepMetadataExtraction, EDUREP_EXTRACTION_OBJECTIVE


class EdurepJsonSearchResourceManager(models.Manager):

    def extract_seeds(self, latest_update):
        queryset = self.get_queryset().filter(
            since__date__gte=latest_update.date(),
            status=200,
            is_extracted=False
        )

        metadata_objective = {
            "@": "$.items",
            "external_id": "$.uuid",
            "state": EdurepMetadataExtraction.get_record_state
        }
        metadata_objective.update(EDUREP_EXTRACTION_OBJECTIVE)
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


class EdurepJsonSearchResource(HarvestHttpResource):

    URI_TEMPLATE = "https://wszoeken.edurep.kennisnet.nl/jsonsearch?" \
                    "query=%2A%20AND%20about.repository%20exact%20" \
                    + "{}" + \
                    "%20AND%20%28schema%3AeducationalLevel.schema%3AtermCode%20exact%20" \
                    "bbbd99c6-cf49-4980-baed-12388f8dcff4%20OR%20schema%3AeducationalLevel.schema%3A" \
                    "termCode%20exact%20be140797-803f-4b9e-81cc-5572c711e09c%29"

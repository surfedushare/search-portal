from django.conf import settings
from django.db import migrations

from core.constants import Repositories
from sharekit.extraction import SHAREKIT_EXTRACTION_OBJECTIVE, SharekitMetadataExtraction


def migrate_objective_to_extraction_mapping(apps, schema_editor):
    ExtractionMapping = apps.get_model("core.ExtractionMapping")
    ExtractionMethod = apps.get_model("core.ExtractionMethod")
    MethodExtractionField = apps.get_model("core.MethodExtractionField")
    JSONExtractionField = apps.get_model("core.JSONExtractionField")
    ObjectiveProperty = apps.get_model("core.ObjectiveProperty")

    mapping = ExtractionMapping.objects.create(name="Sharekit", repository=Repositories.SHAREKIT, root="$.data")
    sharekit_objective = {
        "external_id": "$.id",
        "state": SharekitMetadataExtraction.get_record_state
    }
    sharekit_objective.update(SHAREKIT_EXTRACTION_OBJECTIVE)

    for key, value in sharekit_objective.items():
        if isinstance(value, str):
            json_field, created = JSONExtractionField.objects.get_or_create(path=value)
            ObjectiveProperty.objects.create(
                json_field=json_field,
                mapping=mapping,
                property=key if not key.startswith("#") else key[1:],
                is_context=key.startswith("#")
            )
        else:
            processor, method = value.__qualname__.split(".")
            extraction_method, created = ExtractionMethod.objects.get_or_create(processor=processor, method=method)
            method_field, created = MethodExtractionField.objects.get_or_create(method=extraction_method)
            ObjectiveProperty.objects.create(
                method_field=method_field,
                mapping=mapping,
                property=key if not key.startswith("#") else key[1:],
                is_context=key.startswith("#")
            )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_dynamic_extraction'),
    ]

    operations = [
        migrations.RunPython(
            migrate_objective_to_extraction_mapping,
            migrations.RunPython.noop
        )
    ]

from django.conf import settings
from django.db import migrations

from core.constants import Repositories
from sharekit.extraction import SHAREKIT_EXTRACTION_OBJECTIVE, SharekitMetadataExtraction


def migrate_objective_to_extraction_mapping(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_dynamic_extraction'),
    ]

    operations = [
        migrations.RunPython(
            migrate_objective_to_extraction_mapping,
            migrations.RunPython.noop
        )
    ]

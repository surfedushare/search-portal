from datetime import datetime

from django.conf import settings
from django.db import migrations
from django.utils.timezone import make_aware

from core.models import Dataset, Harvest


NEW_DATASET_NAME = "gamma"


def _clone_dataset(instance, name):
    current_harvests = list(Harvest.objects.filter(dataset=instance))
    instance.pk = None
    instance.name = name
    instance.save(force_insert=True)
    for harvest in current_harvests:
        harvest.pk = None
        harvest.latest_update_at = make_aware(datetime(year=1970, month=1, day=1))
        harvest.dataset = instance
        harvest.purge_at = None
        harvest.harvested_at = None
        harvest.clean()
        harvest.save(force_insert=True)
    return instance


def create_new_dataset(apps, schema_editor):
    """
    Go over all indicated metadata fields and make copies
    """
    if settings.PROJECT != "edusources":
        return
    # Load latest dataset and harvests. Deactivate old datasets
    current_dataset = Dataset.objects.filter(is_active=True).last()
    if not current_dataset:
        return
    Dataset.objects.filter(is_active=True).update(is_active=False)
    # Clone current database with new name
    _clone_dataset(current_dataset, "gamma")


def undo_create_new_dataset(apps, schema_editor):
    if settings.PROJECT != "edusources":
        return
    Dataset.objects.filter(name="gamma").delete()
    Dataset.objects.filter(name="beta").update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_buas_source'),
    ]

    operations = [
        migrations.operations.RunPython(
            create_new_dataset,
            undo_create_new_dataset
        )
    ]

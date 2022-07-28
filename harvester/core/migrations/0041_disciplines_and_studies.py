from datetime import datetime

from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import make_aware

from core.models import Dataset, Harvest


properties_to_rename = {
    "learning_material_themes": "learning_material_disciplines",
    "disciplines": "studies"
}


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


def update_harvest_objective_and_create_new_dataset(apps, schema_editor):
    """
    Rename all harvest objective configuration. For NPPO this is all we need to do.
    Then for Edusources go over all indicated metadata fields and make copies
    """
    ObjectiveProperty = apps.get_model("core.ObjectiveProperty")
    for current, future in properties_to_rename.items():
        ObjectiveProperty.objects.filter(property=current).update(property=future)
    ExtractionMethod = apps.get_model("core.ExtractionMethod")
    for current, future in properties_to_rename.items():
        ExtractionMethod.objects.filter(method=f"get_{current}").update(method=f"get_{future}")
    # Early exit for NPPO
    if settings.PROJECT != "edusources":
        return
    # Load latest dataset and harvests. Deactivate old datasets
    current_dataset = Dataset.objects.filter(is_active=True).last()
    if not current_dataset:
        return
    Dataset.objects.filter(is_active=True).update(is_active=False, is_latest=False)
    # Clone current database with new name
    _clone_dataset(current_dataset, "gamma")


def undo_update_harvest_objective_and_create_new_dataset(apps, schema_editor):
    ObjectiveProperty = apps.get_model("core.ObjectiveProperty")
    for current, future in properties_to_rename.items():
        ObjectiveProperty.objects.filter(property=future).update(property=current)
    ExtractionMethod = apps.get_model("core.ExtractionMethod")
    for current, future in properties_to_rename.items():
        ExtractionMethod.objects.filter(method=f"get_{future}").update(method=f"get_{current}")
    # Early exit for NPPO
    if settings.PROJECT != "edusources":
        return
    Dataset.objects.filter(name="gamma").delete()
    Dataset.objects.filter(name="beta").update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_buas_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectiveproperty',
            name='property',
            field=models.CharField(choices=[('aggregation_level', 'aggregation_level'), ('analysis_allowed', 'analysis_allowed'), ('authors', 'authors'), ('copyright', 'copyright'), ('copyright_description', 'copyright_description'), ('description', 'description'), ('doi', 'doi'), ('external_id', 'external_id'), ('files', 'files'), ('from_youtube', 'from_youtube'), ('has_parts', 'has_parts'), ('ideas', 'ideas'), ('is_part_of', 'is_part_of'), ('is_restricted', 'is_restricted'), ('keywords', 'keywords'), ('language', 'language'), ('learning_material_disciplines', 'learning_material_disciplines'), ('lom_educational_levels', 'lom_educational_levels'), ('lowest_educational_level', 'lowest_educational_level'), ('material_types', 'material_types'), ('mime_type', 'mime_type'), ('parties', 'parties'), ('publisher_date', 'publisher_date'), ('publisher_year', 'publisher_year'), ('publishers', 'publishers'), ('research_object_type', 'research_object_type'), ('research_themes', 'research_themes'), ('state', 'state'), ('studies', 'studies'), ('technical_type', 'technical_type'), ('title', 'title'), ('url', 'url')], max_length=50),
        ),
        migrations.operations.RunPython(
            update_harvest_objective_and_create_new_dataset,
            undo_update_harvest_objective_and_create_new_dataset
        )
    ]

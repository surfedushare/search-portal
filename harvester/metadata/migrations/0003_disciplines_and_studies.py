from django.db import migrations

from metadata.models import MetadataField, MetadataTranslation


fields_to_copy = {
    "learning_material_themes": "learning_material_disciplines",
    "learning_material_themes_normalized": "learning_material_disciplines_normalized",
    "disciplines": "studies"
}


def _clone_metadata_value(instance, field, parent):
    instance.pk = None
    instance.translation = MetadataTranslation.objects.create(
        en=instance.translation.en,
        nl=instance.translation.nl,
        is_fuzzy=instance.translation.is_fuzzy
    )
    instance.field = field
    instance.parent = parent
    instance.save(force_insert=True)


def copy_to_disciplines_and_studies(apps, schema_editor):
    """
    Go over all indicated metadata fields and make copies
    """
    for field in MetadataField.objects.filter(name__in=fields_to_copy.keys()):
        root_values = list(field.metadatavalue_set.filter(parent__isnull=True))
        field.name = fields_to_copy[field.name]
        field.pk = None
        field.translation = MetadataTranslation.objects.create(
            en=field.translation.en,
            nl=field.translation.nl,
            is_fuzzy=field.translation.is_fuzzy

        )
        field.save(force_insert=True)
        for root_value in root_values:
            child_values = root_value.get_children()
            _clone_metadata_value(root_value, field, None)
            for child_value in child_values:
                _clone_metadata_value(child_value, field, root_value)


def undo_copy_to_disciplines_and_studies(apps, schema_editor):
    MetadataField.objects.filter(name__in=fields_to_copy.values()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0002_load_data'),
    ]

    operations = [
        migrations.operations.RunPython(
            copy_to_disciplines_and_studies,
            undo_copy_to_disciplines_and_studies
        )
    ]

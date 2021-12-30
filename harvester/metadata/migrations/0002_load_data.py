import os
import json

from django.conf import settings
from django.db import migrations


def _load_metadata_values(field, values, MetadataValue, MetadataTranslation, parent=None):
    for value in values:
        translation = MetadataTranslation.objects.create(**value["title_translations"])
        value_instance, created = MetadataValue.objects.get_or_create(
            field=field,
            value=value["external_id"],
            defaults={
                "name": value["name"],
                "translation": translation,
                "is_hidden": value["is_hidden"],
                "is_manual": value["is_manual"],
                "parent": parent,
                "lft": 0,
                "rght": 0,
                "level": 0,
                "tree_id": 0
            }
        )
        _load_metadata_values(field, value["children"], MetadataValue, MetadataTranslation, parent=value_instance)


def load_filter_categories_data(apps, schema_editor):
    # Load models
    MetadataField = apps.get_model("metadata.MetadataField")
    MetadataValue = apps.get_model("metadata.MetadataValue")
    MetadataTranslation = apps.get_model("metadata.MetadataTranslation")
    # Load data
    json_file_path = os.path.join(
        settings.BASE_DIR,
        "metadata", "migrations",
        f"0000_{settings.PROJECT}_filter_categories.json"
    )
    with open(json_file_path) as json_file:
        data = json.load(json_file)
    for field in data:
        translation = MetadataTranslation.objects.create(**field["title_translations"])
        field_instance = MetadataField.objects.create(
            name=field["external_id"],
            translation=translation,
            is_hidden=field["is_hidden"],
            is_manual=field["is_manual"],
            english_as_dutch=field["external_id"] in ["authors.name.keyword", "publishers.keyword"]
        )
        _load_metadata_values(field_instance, field["children"], MetadataValue, MetadataTranslation)
    # Rebuilds the tree, we can only do that with the "full" MetadataValue manager
    from metadata.models import MetadataValue
    MetadataValue.objects.rebuild()


def delete_filter_categories_data(apps, schema_editor):
    # Load models
    MetadataField = apps.get_model("metadata.MetadataField")
    MetadataValue = apps.get_model("metadata.MetadataValue")
    MetadataTranslation = apps.get_model("metadata.MetadataTranslation")
    MetadataField.objects.all().delete()
    MetadataValue.objects.all().delete()
    MetadataTranslation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            load_filter_categories_data,
            delete_filter_categories_data
        ),
    ]

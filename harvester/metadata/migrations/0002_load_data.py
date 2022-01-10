import os
import json

from django.conf import settings
from django.db import migrations


def _duplicate_themes_field(field_name, MetadataField, MetadataValue):
    themes_field = MetadataField.objects.get(name=field_name)
    themes_field.id = None
    themes_field.name += "_normalized"
    field_translation = themes_field.translation
    field_translation.id = None
    field_translation.save()
    themes_field.translation = field_translation
    themes_field.translation.save()
    themes_field.save()
    for theme_value in MetadataValue.objects.filter(field__name=field_name, parent=None):
        theme_value.field_id = themes_field.id
        value_translation = theme_value.translation
        value_translation.id = None
        value_translation.save()
        theme_value.translation = value_translation
        theme_value.id = None
        theme_value.save()


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
    # Duplicates the themes field on Edusources to create a normalized version
    if settings.PROJECT == "edusources":
        _duplicate_themes_field("learning_material_themes", MetadataField, MetadataValue)
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

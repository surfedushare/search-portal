from django.db import migrations


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

    operations = []

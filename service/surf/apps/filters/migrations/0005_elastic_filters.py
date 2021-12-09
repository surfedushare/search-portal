from django.db import migrations

from surf.vendor.elasticsearch.api import ElasticSearchApiClient


def migrate_edurep_filters_to_elastic(apps, schema_editor):
    MpttFilterItem = apps.get_model("filters.MpttFilterItem")
    for filter_item in MpttFilterItem.objects.filter(parent__isnull=True):
        filter_item.external_id = ElasticSearchApiClient.translate_external_id_to_elastic_type(filter_item.external_id)
        filter_item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('filters', '0004_allow_identical_external_ids'),
    ]

    operations = [
        migrations.RunPython(
            migrate_edurep_filters_to_elastic,
            migrations.RunPython.noop
        )
    ]

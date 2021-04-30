from datetime import datetime, timedelta

from django.conf import settings
from django.apps import apps
from django.utils.timezone import make_aware
from django.core.management.base import BaseCommand

from core.models import Dataset, DatasetVersion, Document, ElasticIndex


class Command(BaseCommand):
    """
    A convenience command to delete any resources that are erroneous or considered stale
    """

    resources = {
        "core.FileResource": "file",
        "core.TikaResource": "tika"
    }

    def handle(self, **options):
        purge_time = make_aware(datetime.now()) - timedelta(**settings.DATA_RETENTION_PURGE_AFTER)
        # Delete DatasetVersions that are not in use and overdue
        stale_dataset_versions = DatasetVersion.objects.filter(created_at__lte=purge_time, is_current=False)
        stale_dataset_versions.delete()
        # Keep some old versions for each dataset around and destroy the rest
        for dataset in Dataset.objects.all():
            current_dataset_versions = DatasetVersion.objects \
                .filter(created_at__lte=purge_time, is_current=True, dataset=dataset) \
                .order_by("-created_at")
            if current_dataset_versions.count() > settings.DATA_RETENTION_KEEP_VERSIONS:
                for old_dataset_version in current_dataset_versions[settings.DATA_RETENTION_KEEP_VERSIONS:]:
                    old_dataset_version.delete()
        # Now go over all resources and delete old ones without matching documents
        for resource_model, pipeline_phase in self.resources.items():
            model = apps.get_model(resource_model)
            for resource in model.objects.filter(purge_at__lte=purge_time):
                document_filter = {
                    f"properties__pipeline__{pipeline_phase}__resource__0": resource_model.lower(),
                    f"properties__pipeline__{pipeline_phase}__resource__1": resource.id
                }
                if not Document.objects.filter(**document_filter).exists():
                    resource.delete()
        # Finally delete all ElasticIndex without a DatasetVersion (this clears remote indices as well)
        for index in ElasticIndex.objects.filter(dataset_version__isnull=True):
            index.delete()

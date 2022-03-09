from datetime import datetime, timedelta

from django.conf import settings
from django.apps import apps
from django.utils.timezone import make_aware
from django.core.management.base import BaseCommand

from core.models import Dataset, DatasetVersion, Document, ElasticIndex, Extension


class Command(BaseCommand):
    """
    A convenience command to delete any data that is considered stale
    """

    resources = {
        "core.HttpTikaResource": "tika",
        "core.ExtructResource": "extruct",
        "core.YoutubeThumbnailResource": "youtube_preview",
        "core.PdfThumbnailResource": "pdf_preview",
    }

    def handle(self, **options):
        purge_time = make_aware(datetime.now()) - timedelta(**settings.DATA_RETENTION_PURGE_AFTER)
        # Delete DatasetVersions that are not in use and overdue
        for dataset in Dataset.objects.all():
            stale_dataset_versions = DatasetVersion.objects.get_stale_versions(purge_time, dataset)
            for stale_dataset_version in stale_dataset_versions:
                stale_dataset_version.delete()
        # Delete old is_addition Extensions that got deleted
        Extension.objects.filter(deleted_at__lte=purge_time).delete()
        # Now go over all resources and delete old ones without matching documents
        for resource_model, pipeline_phase in self.resources.items():
            model = apps.get_model(resource_model)
            for resource in model.objects.filter(purge_at__lte=purge_time):
                document_filter = {
                    f"pipeline__{pipeline_phase}__resource": resource_model.lower(),
                    f"pipeline__{pipeline_phase}__id": resource.id
                }
                if not Document.objects.filter(**document_filter).exists():
                    resource.delete()
        # Finally delete all ElasticIndex without a DatasetVersion (this clears remote indices as well)
        for index in ElasticIndex.objects.filter(dataset_version__isnull=True):
            index.delete()

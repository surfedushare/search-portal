from collections import defaultdict
from itertools import groupby
from functools import reduce

from django.conf import settings
from django.db import models, transaction

from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin
from datagrowth.utils import ibatch

from core.models.datatypes.extension import Extension


class Dataset(DocumentCollectionMixin, CollectionBase):
    """
    The most overarching model for storing learning materials.
    It's assumed that any Documents within a single Dataset have a similar schema.
    Meaning that any key in a Document's properties will be present in any other Document of the same Dataset.
    """

    is_active = models.BooleanField(default=False)
    is_latest = models.BooleanField(default=False)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.dataset = self
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)

    @classmethod
    def get_name(cls):  # adheres to Datagrowth protocol for easy data loads
        return "dataset"

    @transaction.atomic
    def create_new_version(self, excluded_specs=None):
        excluded_specs = excluded_specs or []
        current_version = DatasetVersion.objects.get_current_version()
        new_version = self.versions.create(version=settings.VERSION, is_current=False)

        for harvest in self.harvest_set.all():
            if current_version and harvest.source.spec not in excluded_specs and not harvest.should_purge():
                collection = current_version.collection_set.filter(name=harvest.source.spec).last()
                if collection:
                    new_version.copy_collection(collection)

        return new_version

    def get_earliest_harvest_date(self):
        latest_harvest = self.harvest_set.order_by("harvested_at").first()
        return latest_harvest.harvested_at if latest_harvest else None


class DatasetVersionManager(models.Manager):

    def get_latest_version(self, dataset=None, dataset_name=None):
        filters = {
            "version": settings.VERSION
        }
        if dataset:
            filters.update({"dataset": dataset})
        elif dataset_name:
            filters.update({"dataset__name": dataset_name})
        return super().get_queryset().filter(**filters).last()

    def get_current_version(self):
        return super().get_queryset().filter(is_current=True).last()

    @staticmethod
    def reduce_version_integer(dataset_version):
        def _reduce_version_integer(value, ix_element):
            ix, element = ix_element
            multiplier = pow(1000, ix)
            integer = multiplier * int(element) if multiplier else int(element)
            return value + integer
        version_split = dataset_version.version.split(".")
        version_split.reverse()
        result = reduce(_reduce_version_integer, enumerate(version_split), 0)
        return result

    def get_stale_versions(self, purge_time, dataset):
        queryset = self.get_queryset().filter(dataset=dataset, is_current=False).order_by("version", "created_at")
        grouped_versions = {
            group: list(versions)
            for group, versions in groupby(queryset, self.reduce_version_integer)
        }
        version_keys = sorted(grouped_versions.keys(), reverse=True)
        retained_versions = []
        stale_versions = []
        for version_key in version_keys:
            dataset_versions = grouped_versions[version_key]
            if len(retained_versions) < settings.DATA_RETENTION_KEEP_VERSIONS:
                retained_versions.append(dataset_versions.pop())
                stale_versions += dataset_versions
            else:
                stale_versions += dataset_versions
        return [
            stale_version for stale_version in stale_versions
            if stale_version.created_at <= purge_time
        ]


class DatasetVersion(models.Model):

    objects = DatasetVersionManager()

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=False, blank=False, related_name="versions")
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=50, null=False, blank=True)

    def __str__(self):
        return "{} (v={}, id={})".format(self.dataset.name, self.version, self.id)

    def copy_collection(self, collection):
        Document = collection.get_document_model()
        source_id = collection.id
        collection.pk = None
        collection.id = None
        collection.dataset_version = self
        collection.save()
        for batch in ibatch(Document.objects.filter(collection_id=source_id), batch_size=100):
            for doc in batch:
                doc.collection_id = collection.id
                doc.dataset_version = self
                doc.pk = None
                doc.id = None
            Document.objects.bulk_create(batch)
        return collection

    def get_elastic_documents_by_language(self):
        by_language = defaultdict(list)
        for document in self.document_set.select_related("extension").all():
            language = document.get_language()
            if language not in settings.ELASTICSEARCH_ANALYSERS:
                language = "unk"
            by_language[language] += list(document.to_search())
        for extension in Extension.objects.filter(is_addition=True):
            language = extension.get_language()
            if language not in settings.ELASTICSEARCH_ANALYSERS:
                language = "unk"
            by_language[language] += list(extension.to_search())
        return by_language

    def set_current(self):
        DatasetVersion.objects.all().update(is_current=False)
        self.is_current = True
        self.save()

    class Meta:
        get_latest_by = "-created_at"

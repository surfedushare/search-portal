from collections import defaultdict

from django.db import models

from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin
from core.models.datatypes.document import Document, document_delete_handler


class Dataset(DocumentCollectionMixin, CollectionBase):
    """
    The most overarching model for storing learning materials.
    It's assumed that any Documents within a single Dataset have a similar schema.
    Meaning that any key in a Document's properties will be present in any other Document of the same Dataset.
    """

    is_active = models.BooleanField(default=False)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection)
        doc.dataset = self
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)

    @classmethod
    def get_name(cls):  # adheres to Datagrowth protocol for easy data loads
        return "dataset"

    def reset(self):
        """
        Resets all related harvest instances and deletes all data, but retains all cache
        """
        models.signals.post_delete.disconnect(
            document_delete_handler,
            sender=Document,
            dispatch_uid="document_delete"
        )
        self.collection_set.all().delete()
        for harvest in self.harvest_set.all():
            harvest.reset()
        models.signals.post_delete.connect(
            document_delete_handler,
            sender=Document,
            dispatch_uid="document_delete"
        )

    def get_earliest_harvest_date(self):
        latest_harvest = self.harvest_set.order_by("harvested_at").first()
        return latest_harvest.harvested_at if latest_harvest else None


class DatasetVersion(models.Model):

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=False, blank=False, related_name="versions")
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=50, null=False, blank=True)

    def __str__(self):
        return "{} (v={}, id={})".format(self.dataset.name, self.version, self.id)

    def get_elastic_documents_by_language(self):
        by_language = defaultdict(list)
        for document in self.document_set.all():
            language = document.get_language()
            by_language[language] += list(document.to_search())
        return by_language

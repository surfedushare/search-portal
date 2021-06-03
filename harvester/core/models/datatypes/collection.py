from django.db import models

from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin


class Collection(DocumentCollectionMixin, CollectionBase):
    """
    Represents a set as used by the OAI-PMH protocol.
    These sets are logically collections of documents.

    N.B.: Collection has a special meaning within the search portal.
    They are manually curated groups of learning materials.
    """

    dataset_version = models.ForeignKey("DatasetVersion", blank=True, null=True, on_delete=models.CASCADE)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection or self)
        doc.dataset_version = self.dataset_version
        return doc

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)

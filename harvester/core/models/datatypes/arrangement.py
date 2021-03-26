from collections import Iterator
import logging

from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.utils.functional import cached_property

from datagrowth import settings as datagrowth_settings
from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin
from datagrowth.utils import ibatch


logger = logging.getLogger("harvester")


class Arrangement(DocumentCollectionMixin, CollectionBase):
    """
    When people search in the portal this is what they find.
    The Arrangement is in other words responsible for generating the Elastic Search Document.
    It does this through possibly multiple Datagrowth Documents.
    A Datagrowth Document is akin to a file.
    """

    # dataset = models.ForeignKey("Dataset", blank=True, null=True, on_delete=models.CASCADE)
    # collection = models.ForeignKey("Collection", blank=True, null=True, on_delete=models.CASCADE)
    meta = postgres_fields.JSONField(default=dict)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def init_document(self, data, collection=None):
        doc = super().init_document(data, collection=collection or self.collection)
        doc.dataset = self.dataset
        doc.arrangement = self
        return doc

    def update(self, data, by_reference, validate=True, batch_size=32, collection=None):
        collection = collection or self
        Document = collection.get_document_model()
        assert isinstance(data, (Iterator, list, tuple, dict, Document)), \
            f"Collection.update expects data to be formatted as iteratable, dict or {type(Document)} not {type(data)}"

        count = 0
        for updates in ibatch(data, batch_size=batch_size):
            # First we bulk update by getting all objects whose identifier value match any update's "by" value
            # and then updating these source objects.
            # One update object can potentially target multiple sources
            # if multiple objects with an identifier of "by" exist.
            updated = set()
            hashed = {update[by_reference]: update for update in updates}
            sources = {source[by_reference]: source for source in collection.documents.filter(
                reference__in=hashed.keys())}
            for source in sources.values():
                source.update(hashed[source.reference], validate=validate)
                count += 1
                updated.add(source.reference)
            Document.objects.bulk_update(
                sources.values(),
                ["properties"],
                batch_size=datagrowth_settings.DATAGROWTH_MAX_BATCH_SIZE
            )
            # After all updates we add all data that hasn't been used in any update operation
            additions = [update for identify, update in hashed.items() if identify not in updated]
            if len(additions):
                count += self.add(additions, validate=validate, batch_size=batch_size, collection=collection)

        return count

    @cached_property
    def base_document(self):
        text_documents = self.documents.exclude(properties__file_type="video")
        video_documents = self.documents.filter(properties__file_type="video")
        base_document = video_documents.first()
        if base_document is None:
            base_document = text_documents.first()
        return base_document

    def store_language(self):
        self.meta["language"] = self.base_document.get_language() if self.base_document else "unk"
        self.save()

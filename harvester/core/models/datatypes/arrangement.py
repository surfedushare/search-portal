from collections import Iterator

from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.utils.timezone import now

from datagrowth import settings as datagrowth_settings
from datagrowth.datatypes import CollectionBase, DocumentCollectionMixin
from datagrowth.utils import ibatch


class Arrangement(DocumentCollectionMixin, CollectionBase):
    """
    When people search in the portal this is what they find.
    The Arrangement is in other words responsible for generating the Elastic Search Document.
    It does this through possibly multiple Datagrowth Documents.
    A Datagrowth Document is akin to a file.
    """

    dataset = models.ForeignKey("Dataset", blank=True, null=True, on_delete=models.CASCADE)
    collection = models.ForeignKey("Collection", blank=True, null=True, on_delete=models.CASCADE)
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

    def to_search(self):

        text_documents = self.documents.exclude(properties__file_type="video")
        texts = []
        for doc in text_documents:
            texts.append(doc.properties["text"])
        text = "\n\n".join(texts)

        video_documents = self.documents.filter(properties__file_type="video")
        transcriptions = []
        for doc in video_documents:
            if doc.properties["text"] is None:
                continue
            transcriptions.append(doc.properties["text"])
        transcription = "\n\n".join(transcriptions)

        base_document = video_documents.first()
        if base_document is None:
            base_document = text_documents.first()

        # Elastic Search actions get streamed to the Elastic Search service
        elastic_search_action = {
            'title': base_document.properties['title'],
            'text': text,
            'transcription': transcription,
            'url': base_document.properties['url'],
            'external_id': base_document.properties['external_id'],
            'disciplines': base_document.properties['disciplines'],
            'educational_levels': base_document.properties['educational_levels'],
            'lom_educational_levels': base_document.properties['lom_educational_levels'],
            'author': base_document.properties['author'],
            'authors': base_document.properties['authors'],
            'publishers': base_document.properties['publishers'],
            'description': base_document.properties['description'],
            'publisher_date': base_document.properties['publisher_date'],
            'copyright': base_document.properties['copyright'],
            'aggregation_level': base_document.properties['aggregation_level'],
            'language': base_document.get_language(),
            'title_plain': base_document.properties['title'],
            'text_plain': text,
            'transcription_plain': transcription,
            'keywords': self.meta['keywords'],
            'file_type': base_document['file_type'] if 'file_type' in base_document.properties else 'unknown',
            'mime_type': base_document['mime_type'],
            'suggest': base_document['title'].split(" ") if base_document['title'] else [],
            '_id': self.meta['reference_id'],
            'oaipmh_set': self.collection.name,
            'arrangement_collection_name': self.collection.name  # TODO: remove this once everything uses oaipmh_set
        }
        if self.deleted_at:
            elastic_search_action["_op_type"] = "delete"
        return elastic_search_action

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

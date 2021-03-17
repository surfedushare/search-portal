from collections import Iterator
import logging

from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.utils.timezone import now
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

    @staticmethod
    def get_search_document_details(reference_id, url, title, text, transcription, mime_type, file_type,
                                    is_part_of=None, has_part=None):
        has_part = has_part or []
        return {
            '_id': reference_id,
            'title': title,
            'text': text,
            'transcription': transcription,
            'url': url,
            'title_plain': title,
            'text_plain': text,
            'transcription_plain': transcription,
            'file_type': file_type,
            'mime_type': mime_type,
            'has_part': has_part,
            'is_part_of': is_part_of,
            'suggest_completion': title.split(" ") if title else [],
            'suggest_phrase': text
        }

    def get_search_document_base(self):
        """
        This method returns either a delete action or a partial upsert action.
        If it returns a partial update action it will only fill out all data
        that's the same for all documents coming from this Arrangement.
        Only the reference_id gets added for both partial update and delete actions

        :return: Elastic Search partial update or delete action
        """
        # First we fill out all data we know from the Arrangement or we have an early return for deletes
        # and unknown data
        base = {
            "language": self.meta.get("language", "unk"),
        }
        if self.deleted_at:
            base["_id"] = self.meta["reference_id"]
            base["_op_type"] = "delete"
            return base
        elif not self.base_document:
            return base
        # Then we enhance the data with any data coming from the base document belonging to the arrangement
        base.update({
            'external_id': self.base_document.properties['external_id'],
            'disciplines': self.base_document.properties['disciplines'],
            'educational_levels': self.base_document.properties['educational_levels'],
            'lom_educational_levels': self.base_document.properties['lom_educational_levels'],
            'ideas': self.base_document.properties.get('ideas', []),
            'authors': self.base_document.properties['authors'],
            'publishers': self.base_document.properties['publishers'],
            'description': self.base_document.properties['description'],
            'publisher_date': self.base_document.properties['publisher_date'],
            'copyright': self.base_document.properties['copyright'],
            'aggregation_level': self.base_document.properties['aggregation_level'],
            'preview_path': self.base_document.properties.get('preview_path', None),
            'analysis_allowed': self.base_document.properties.get('analysis_allowed', False),
            'keywords': self.meta['keywords'],
            'oaipmh_set': self.collection.name,
        })
        return base

    def to_search(self):

        elastic_base = self.get_search_document_base()

        if self.deleted_at:
            yield elastic_base
            return

        # Gather text from text media
        text_documents = self.documents.exclude(properties__file_type="video")
        texts = []
        for doc in text_documents:
            texts.append(doc.properties["text"])
        text = "\n\n".join(texts)

        # Gather text from video media
        video_documents = self.documents.filter(properties__file_type="video")
        transcriptions = []
        for doc in video_documents:
            if doc.properties["text"] is None:
                continue
            transcriptions.append(doc.properties["text"])
        transcription = "\n\n".join(transcriptions)

        # Then we yield a Elastic Search document for the Arrangement as a whole
        elastic_details = self.get_search_document_details(
            self.meta["reference_id"],
            self.base_document["url"],
            self.base_document["title"],
            text,
            transcription,
            self.base_document["mime_type"],
            self.base_document["file_type"],
            is_part_of=self.base_document.properties.get("is_part_of", None),
            has_part=self.base_document.properties.get("has_part", [])
        )
        elastic_details.update(elastic_base)
        yield elastic_details

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

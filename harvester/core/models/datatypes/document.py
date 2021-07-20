from mimetypes import guess_type
from copy import copy

from django.db import models

from datagrowth.datatypes import DocumentBase


PRIVATE_PROPERTIES = ["pipeline", "from_youtube", "lowest_educational_level"]


class DocumentManager(models.Manager):

    def build_from_seed(self, seed, collection=None, metadata_pipeline_key=None):
        url = seed.get("url", None)
        mime_type = seed.get("mime_type", None)  # TODO: mime type redundant?
        if mime_type is None and url:
            mime_type, encoding = guess_type(url)

        properties = copy(seed)  # TODO: use setters that update the pipeline?
        properties["mime_type"] = mime_type
        properties["id"] = seed["external_id"]
        properties["language"] = {
            "metadata": seed.get("language", None)
        }
        properties["suggest"] = seed["title"]

        metadata_pipeline = properties.pop(metadata_pipeline_key, None)
        document = Document(properties=properties, collection=collection, pipeline={"metadata": metadata_pipeline})
        if collection:
            document.dataset_version = collection.dataset_version
        document.clean()
        return document


class Document(DocumentBase):

    objects = DocumentManager()

    dataset_version = models.ForeignKey("DatasetVersion", blank=True, null=True, on_delete=models.CASCADE)
    pipeline = models.JSONField(default=dict, blank=True)
    # NB: Collection foreign key is added by the base class

    def get_language(self):
        for field in ['metadata', 'from_text', 'from_title']:
            if field in self.properties['language']:
                language = self.properties['language'][field]
                if language is not None:
                    return language
        return "unk"

    def get_search_document_extras(self, reference_id, title, text):
        extras = {
            '_id': reference_id,
            "language": self.get_language(),
            'suggest_completion': title.split(" ") if title else [],
            'harvest_source': self.collection.name,
            'suggest_phrase': text
        }
        return extras

    def to_search(self):
        elastic_base = copy(self.properties)
        elastic_base.pop("language")
        for private_property in PRIVATE_PROPERTIES:
            elastic_base.pop(private_property, False)
        elastic_details = self.get_search_document_extras(
            self.properties["external_id"],
            self.properties["title"],
            self.properties.get("text", None)
        )
        elastic_details.update(elastic_base)
        yield elastic_details

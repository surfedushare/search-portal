from copy import copy

from django.db import models

from datagrowth.datatypes import DocumentBase


PRIVATE_PROPERTIES = ["pipeline", "from_youtube", "lowest_educational_level"]


class Document(DocumentBase):

    dataset_version = models.ForeignKey("DatasetVersion", blank=True, null=True, on_delete=models.CASCADE)
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
        for private_property in PRIVATE_PROPERTIES:
            elastic_base.pop(private_property)
        elastic_details = self.get_search_document_extras(
            self.properties["external_id"],
            self.properties["title"],
            self.properties["text"]
        )
        elastic_details.update(elastic_base)
        yield elastic_details

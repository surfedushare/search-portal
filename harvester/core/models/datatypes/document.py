from django.db import models
from django.apps import apps

from datagrowth.datatypes import DocumentBase, DocumentPostgres
from core.utils.previews import delete_previews


class Document(DocumentPostgres, DocumentBase):

    dataset = models.ForeignKey("Dataset", blank=True, null=True, on_delete=models.CASCADE)
    dataset_version = models.ForeignKey("DatasetVersion", blank=True, null=True, on_delete=models.CASCADE)
    # NB: Collection foreign key is added by the base class

    def get_language(self):
        for field in ['metadata', 'from_text', 'from_title']:
            if field in self.properties['language']:
                language = self.properties['language'][field]
                if language is not None:
                    return language
        return "unk"

    @staticmethod
    def get_search_document_details(reference_id, url, title, text, transcription, mime_type, file_type,
                                    is_part_of=None, has_parts=None):
        has_parts = has_parts or []
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
            'has_parts': has_parts,
            'has_part': has_parts,  # TODO: remove after migration
            'is_part_of': is_part_of,
            'suggest_completion': title.split(" ") if title else [],
            'suggest_phrase': text
        }

    def get_search_document_base(self):
        """
        This method returns a partial upsert action.

        :return: Elastic Search partial update
        """
        return {
            "language": self.get_language(),
            'external_id': self.properties['external_id'],
            'disciplines': self.properties['disciplines'],
            'educational_levels': self.properties['educational_levels'],
            'lom_educational_levels': self.properties['lom_educational_levels'],
            'ideas': self.properties.get('ideas', []),
            'authors': self.properties['authors'],
            'publishers': self.properties['publishers'],
            'description': self.properties['description'],
            'publisher_date': self.properties['publisher_date'],
            'copyright': self.properties['copyright'],
            'aggregation_level': self.properties['aggregation_level'],
            'preview_path': self.properties.get('preview_path', None),
            'analysis_allowed': self.properties.get('analysis_allowed', False),
            'keywords': self.properties.get('keywords', []),
            'oaipmh_set': self.collection.name,
            'harvest_source': self.collection.name,
        }

    def to_search(self):
        elastic_base = self.get_search_document_base()
        elastic_details = self.get_search_document_details(
            self.properties["external_id"],
            self.properties["url"],
            self.properties["title"],
            self.properties["text"],
            self.properties.get("transcription", None),
            self.properties["mime_type"],
            self.properties["file_type"],
            is_part_of=self.properties.get("is_part_of", None),
            has_parts=self.properties.get("has_parts", [])
        )
        elastic_details.update(elastic_base)
        yield elastic_details


def document_delete_handler(sender, instance, **kwargs):
    preview_path = instance.properties.get("preview_path", None)
    if preview_path:
        delete_previews(preview_path)


models.signals.post_delete.connect(
    document_delete_handler,
    sender=Document,
    dispatch_uid="document_delete"
)

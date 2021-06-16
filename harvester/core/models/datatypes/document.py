from django.db import models

from datagrowth.datatypes import DocumentBase


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

    @staticmethod
    def get_search_document_details(reference_id, url, title, text, mime_type, file_type,
                                    is_part_of=None, has_parts=None):
        has_parts = has_parts or []
        is_part_of = is_part_of or []
        details = {
            '_id': reference_id,
            'title': title,
            'url': url,
            'file_type': file_type,
            'mime_type': mime_type,
            'has_parts': has_parts,
            'is_part_of': is_part_of,
            'suggest_completion': title.split(" ") if title else [],
        }
        if text:
            details.update({
                'text': text,
                'suggest_phrase': text
            })
        return details

    def get_search_document_base(self):
        """
        This method returns a partial upsert action.

        :return: Elastic Search partial update
        """
        return {
            "language": self.get_language(),
            'external_id': self.properties['external_id'],
            'disciplines': self.properties['disciplines'],
            'lom_educational_levels': self.properties['lom_educational_levels'],
            'ideas': self.properties.get('ideas', []),
            'files': self.properties['files'],
            'authors': self.properties['authors'],
            'publishers': self.properties['publishers'],
            'description': self.properties['description'],
            'publisher_date': self.properties['publisher_date'],
            'copyright': self.properties['copyright'],
            'copyright_description': self.properties['copyright_description'],
            'aggregation_level': self.properties['aggregation_level'],
            'preview_path': self.properties.get('preview_path', None),
            'analysis_allowed': self.properties.get('analysis_allowed', False),
            'keywords': self.properties.get('keywords', []),
            'harvest_source': self.collection.name,
            'doi': self.properties.get('doi', None),
        }

    def to_search(self):
        elastic_base = self.get_search_document_base()
        elastic_details = self.get_search_document_details(
            self.properties["external_id"],
            self.properties["url"],
            self.properties["title"],
            self.properties.get("text", None),
            self.properties["mime_type"],
            self.properties["file_type"],
            is_part_of=self.properties.get("is_part_of", []),
            has_parts=self.properties.get("has_parts", [])
        )
        elastic_details.update(elastic_base)
        yield elastic_details

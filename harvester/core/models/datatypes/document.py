from django.db import models

from datagrowth.datatypes import DocumentBase, DocumentPostgres


class Document(DocumentPostgres, DocumentBase):

    dataset = models.ForeignKey("Dataset", blank=True, null=True, on_delete=models.CASCADE)
    # NB: Collection foreign key is added by the base class
    arrangement = models.ForeignKey("Arrangement", blank=True, null=True, on_delete=models.CASCADE)

    def get_language(self):
        for field in ['metadata', 'from_text', 'from_title']:
            if field in self.properties['language']:
                language = self.properties['language'][field]
                if language is not None:
                    return language

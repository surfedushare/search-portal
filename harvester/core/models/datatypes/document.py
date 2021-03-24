from django.db import models
from django.apps import apps

from datagrowth.datatypes import DocumentBase, DocumentPostgres
from core.utils.previews import delete_previews


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


def document_delete_handler(sender, instance, **kwargs):
    for phase, result in instance.properties.get("pipeline", {}).items():
        if not isinstance(result, dict) or not result.get("resource", None):
            continue
        resource_label, resource_id = result["resource"]
        Resource = apps.get_model(resource_label)
        Resource.objects.filter(id=resource_id).delete()
    preview_path = instance.properties.get("preview_path", None)
    if preview_path:
        delete_previews(preview_path)


models.signals.post_delete.connect(
    document_delete_handler,
    sender=Document,
    dispatch_uid="document_delete"
)

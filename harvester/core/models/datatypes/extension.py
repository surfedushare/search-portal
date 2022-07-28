from copy import copy

from django.db import models
from django.utils import timezone

from datagrowth.datatypes import DocumentBase


class Extension(DocumentBase):

    id = models.CharField(primary_key=True, max_length=100)
    dataset_version = models.ForeignKey("DatasetVersion", blank=True, null=True, on_delete=models.CASCADE)
    # NB: Collection foreign key is added by the base class
    is_addition = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    def get_language(self):
        return self.properties.get("language", "unk")

    def to_search(self):
        if self.is_addition and self.deleted_at:
            yield {
                "_op_type": "delete",
                "_id": self.id
            }
            return
        search_base = copy(self.properties)
        title = search_base.get("title", None)
        search_defaults = {
            '_id': self.id,
            "extension": {
                "id": self.id,
                "is_addition": self.is_addition
            },
            "language": self.get_language(),
            'suggest_completion': title.split(" ") if title else [],
            'harvest_source': "nppo",
            'suggest_phrase': None,
            'title': None,
            'text': None,
            'video': None,
            'ideas': [],
            'material_types': [],
            'copyright_description': None,
            'mime_type': None,
            'disciplines': [],
            'url': None,
            'lom_educational_levels': [],
            'description': None,
            'preview_path': None,
            'copyright': None,
            'doi': None,
            'files': [],
            'publishers': [],
            'research_object_type': None,
            'technical_type': None,
            'aggregation_level': None,
            'analysis_allowed': None,
            'publisher_date': None,
            'learning_material_themes_normalized': [],
            'consortium': None
        }
        if "keywords" in search_base:
            search_base["keywords"] = [entry["label"] for entry in search_base["keywords"]]
        themes = search_base.pop("themes", None)
        if themes:
            search_base["research_themes"] = [entry["label"] for entry in themes]
        search_base["is_part_of"] = search_base.pop("parents", [])
        search_base["has_parts"] = search_base.pop("children", [])
        search_defaults.update(search_base)
        yield search_defaults

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at and self.is_addition:
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

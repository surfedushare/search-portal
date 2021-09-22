from copy import copy

from django.db import models

from datagrowth.datatypes import DocumentBase


class Extension(DocumentBase):

    id = models.CharField(primary_key=True, max_length=100)
    dataset_version = models.ForeignKey("DatasetVersion", blank=True, null=True, on_delete=models.CASCADE)
    # NB: Collection foreign key is added by the base class
    is_parent = models.BooleanField(default=False)

    def get_language(self):
        return self.properties.get("language", "unk")

    def to_search(self):
        elastic_base = copy(self.properties)
        title = elastic_base.get("title", None)
        elastic_defaults = {
            '_id': self.id,
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
        }
        if "keywords" in elastic_base:
            elastic_base["keywords"] = [entry["label"] for entry in elastic_base["keywords"]]
        themes = elastic_base.pop("themes", None)
        if themes:
            elastic_base["research_themes"] = [entry["label"] for entry in themes]
        elastic_base["is_part_of"] = elastic_base.pop("parents", [])
        elastic_base["has_parts"] = elastic_base.pop("children", [])
        elastic_defaults.update(elastic_base)
        yield elastic_defaults

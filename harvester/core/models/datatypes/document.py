from copy import copy

from django.db import models

from datagrowth.datatypes import DocumentBase


PRIVATE_PROPERTIES = ["pipeline", "from_youtube", "lowest_educational_level"]


class DocumentManager(models.Manager):

    def build_from_seed(self, seed, collection=None, metadata_pipeline_key=None):
        properties = copy(seed)  # TODO: use setters that update the pipeline?
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
    extension = models.ForeignKey("core.Extension", null=True, on_delete=models.SET_NULL)
    # NB: Collection foreign key is added by the base class

    def get_language(self):
        return self.properties['language'].get("metadata", "unk")

    def get_search_document_extras(self, reference_id, title, text, material_types):
        extras = {
            '_id': reference_id,
            "language": self.get_language(),
            'suggest_completion': title.split(" ") if title else [],
            'harvest_source': self.collection.name,
            'suggest_phrase': text,
            'material_types': material_types
        }
        return extras

    def get_extension_extras(self):
        extension_data = copy(self.extension.properties)
        if "keywords" in extension_data:
            extension_data["keywords"] = [entry["label"] for entry in extension_data["keywords"]]
        themes = extension_data.pop("themes", None)
        if themes:
            extension_data["research_themes"] = [entry["label"] for entry in themes]
        parents = extension_data.pop("parents", None)
        if parents:
            is_part_of = self.properties.get("is_part_of", [])
            is_part_of += parents
            is_part_of = list(set(is_part_of))
            extension_data["is_part_of"] = is_part_of
        children = extension_data.pop("children", None)
        if children:
            has_parts = self.properties.get("has_parts", [])
            has_parts += children
            has_parts = list(set(has_parts))
            extension_data["has_parts"] = has_parts
        return extension_data

    def to_search(self):
        elastic_base = copy(self.properties)
        elastic_base.pop("language")
        if self.extension:
            extension_details = self.get_extension_extras()
            elastic_base.update(extension_details)
        for private_property in PRIVATE_PROPERTIES:
            elastic_base.pop(private_property, False)
        material_types = elastic_base.pop("material_types", None) or ["unknown"]
        elastic_details = self.get_search_document_extras(
            self.properties["external_id"],
            self.properties["title"],
            self.properties.get("text", None),
            material_types=material_types
        )
        elastic_details.update(elastic_base)
        yield elastic_details

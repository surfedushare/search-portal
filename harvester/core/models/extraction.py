from django.db import models

from core.constants import REPOSITORY_CHOICES


OBJECTIVE_PROPERTIES = SHAREKIT_EXTRACTION_OBJECTIVE = {
    "url", "files", "title", "language", "keywords", "description", "mime_type", "technical_type", "material_types",
    "copyright", "copyright_description", "aggregation_level", "authors", "publishers", "publisher_date",
    "lom_educational_levels", "lowest_educational_level", "disciplines", "ideas", "from_youtube", "is_restricted",
    "analysis_allowed", "is_part_of", "has_parts", "doi", "research_object_type", "research_themes", "parties",
}


class ExtractionMethod(models.Model):
    method = models.CharField(max_length=256)
    processor = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.processor}.{self.method}"


class MethodExtractionField(models.Model):
    method = models.ForeignKey(ExtractionMethod, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.method)


class JSONExtractionField(models.Model):
    path = models.CharField(max_length=256)

    def __str__(self):
        return self.path


class ObjectiveProperty(models.Model):

    mapping = models.ForeignKey("ExtractionMapping", on_delete=models.CASCADE)
    json_field = models.ForeignKey(JSONExtractionField, on_delete=models.CASCADE, null=True, blank=True)
    method_field = models.ForeignKey(MethodExtractionField, on_delete=models.CASCADE, null=True, blank=True)
    property = models.CharField(choices=[(prop, prop,) for prop in OBJECTIVE_PROPERTIES], max_length=50)
    is_context = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "objective properties"


class ExtractionMapping(models.Model):

    name = models.CharField(max_length=100, default="develop")
    repository = models.CharField(max_length=50, choices=REPOSITORY_CHOICES)
    root = models.CharField(max_length=256, default="$")

    method_fields = models.ManyToManyField(MethodExtractionField, related_name="+", through=ObjectiveProperty)
    json_fields = models.ManyToManyField(JSONExtractionField, related_name="+", through=ObjectiveProperty)

    def to_objective(self):
        methods = {
            objective_property.property: str(objective_property.method_field)
            for objective_property in ObjectiveProperty.objects.filter(mapping=self, method_field__isnull=False)
        }
        paths = {
            objective_property.property: objective_property.json_field.path
            for objective_property in ObjectiveProperty.objects.filter(mapping=self, json_field__isnull=False)
        }
        return {
            "@": self.root,
            **methods,
            **paths
        }

    def __str__(self):
        return self.name

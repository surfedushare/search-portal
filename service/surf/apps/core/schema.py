from rest_framework.schemas.openapi import AutoSchema
from rest_framework import serializers

from surf.vendor.elasticsearch.serializers import RelationSerializer
from surf.apps.materials.serializers import KeywordsRequestSerializer


class SearchSchema(AutoSchema):

    def _map_field(self, field):
        if field.field_name == "children" and not isinstance(field.parent, RelationSerializer):
            return {
                'type': 'array',
                'items': {
                    "properties": "as parent"
                }
            }
        if field.field_name == "count":
            return super()._map_field(serializers.IntegerField(read_only=True))
        return super()._map_field(field)

    def _map_serializer(self, serializer):
        if isinstance(serializer, KeywordsRequestSerializer):
            return {
                'type': 'string',
                'properties': {}
            }
        return super()._map_serializer(serializer)

    def _get_operation_id(self, path, method):
        operation_id = path.replace("/", "-").strip("-")
        return f"{method.lower()}-{operation_id}"

    def _get_path_parameters(self, path, method):
        if "autocomplete" in path:
            return [
                {
                    "name": "query",
                    "in": "query",
                    "required": True,
                    "description": "The search query you want to autocomplete for.",
                    'schema': {
                        'type': 'string',
                    }
                }
            ]
        if "similarity" in path:
            return [
                {
                    "name": "external_id",
                    "in": "query",
                    "required": True,
                    "description": "The external_id of the document you want similar documents for.",
                    'schema': {
                        'type': 'string',
                    }
                },
                {
                    "name": "language",
                    "in": "query",
                    "required": True,
                    "description": "The language of the document you want similar documents for.",
                    'schema': {
                        'type': 'string',
                    }
                }
            ]
        return super()._get_path_parameters(path, method)

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        if path.startswith("/search"):
            operation["tags"] = ["Full text search"]
        elif path.startswith("/indices"):
            operation["tags"] = ["Document indices"]
        elif path.startswith("/suggestions"):
            operation["tags"] = ["Suggestions"]
        else:
            operation["tags"] = ["default"]
        return operation

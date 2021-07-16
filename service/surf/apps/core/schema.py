from rest_framework.schemas.openapi import AutoSchema
from rest_framework import serializers


class SearchSchema(AutoSchema):

    def _map_field(self, field):
        if field.field_name == "children":
            return {
                'type': 'array',
                'items': {
                    "properties": "as parent"
                }
            }
        if field.field_name == "count":
            return super()._map_field(serializers.IntegerField(read_only=True))
        return super()._map_field(field)

    def _get_operation_id(self, path, method):
        operation_id = path.replace("/", "-").strip("-")
        return f"{method.lower()}-{operation_id}"

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        operation["tags"] = ["Full text search"] if path.startswith("/search") else ["default"]
        return operation

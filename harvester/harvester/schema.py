from rest_framework.schemas.openapi import AutoSchema


class HarvesterSchema(AutoSchema):

    def _get_operation_id(self, path, method):
        operation_id = path.replace("/", "-").strip("-")
        return f"{method.lower()}-{operation_id}"

    def _map_field(self, field):
        if field.field_name == "children":
            return {
                'type': 'array',
                'items': {
                    "properties": "as parent"
                }
            }
        return super()._map_field(field)

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        if path.startswith("/dataset"):
            operation["tags"] = ["Download data"]
        elif path.startswith("/extension"):
            operation["tags"] = ["Extending data"]
        elif path.startswith("/metadata"):
            operation["tags"] = ["Metadata"]
        else:
            operation["tags"] = ["default"]
        return operation

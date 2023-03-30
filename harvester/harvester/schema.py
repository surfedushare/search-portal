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
        if path.startswith("/dataset") or path.startswith("/document"):
            operation["tags"] = ["Download data"]
        elif path.startswith("/extension"):
            operation["tags"] = ["Extending data"]
        elif path.startswith("/search") or path.startswith("/find"):
            operation["tags"] = ["Search"]
            if "search/documents" in path:
                operation["parameters"] += [
                    {
                        "name": "include_filter_counts",
                        "in": "query",
                        "required": False,
                        "description": "When set to 1 the response will include the counts of documents "
                                       "per combination of metadata field and metadata value "
                                       "in the filter_counts property",
                        'schema': {
                            'type': 'number',
                        }
                    }
                ]
        elif path.startswith("/metadata"):
            operation["tags"] = ["Metadata"]
            if "tree" in path:
                operation["parameters"] += [
                    {
                        "name": "max_children",
                        "in": "query",
                        "required": False,
                        "description": "Limits the amount of children returned by this endpoint "
                                       "(mostly useful to speed up responses from the interactive documentation)",
                        'schema': {
                            'type': 'string',
                        }
                    },
                    {
                        "name": "site_id",
                        "in": "query",
                        "required": False,
                        "description": "Specifies which site to get filters for",
                        "default": 1,
                        'schema': {
                            'type': 'string',
                        }
                    }
                ]
            if "field-values" in path:
                operation["parameters"] += [
                    {
                        "name": "site_id",
                        "in": "query",
                        "required": False,
                        "description": "Specifies which site to get filters for",
                        "default": 1,
                        'schema': {
                            'type': 'string',
                        }
                    }
                ]
        else:
            operation["tags"] = ["default"]
        return operation

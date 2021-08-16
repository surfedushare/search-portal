from rest_framework.schemas.openapi import AutoSchema


class HarvesterSchema(AutoSchema):

    def _get_operation_id(self, path, method):
        operation_id = path.replace("/", "-").strip("-")
        return f"{method.lower()}-{operation_id}"

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        print(path)
        if path.startswith("/dataset"):
            operation["tags"] = ["Download data"]
        elif path.startswith("/extension"):
            operation["tags"] = ["Extending data"]
        else:
            operation["tags"] = ["default"]
        return operation

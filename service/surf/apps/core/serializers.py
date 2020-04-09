from html import escape

from rest_framework.serializers import CharField, empty


class EscapeRepresentationCharField(CharField):
    def to_representation(self, value):
        return escape(super().to_representation(value))


class EscapeOnValidationCharField(CharField):
    def run_validation(self, data=empty):
        if isinstance(data, str):
            data = escape(data)
        return super().run_validation(data=data)

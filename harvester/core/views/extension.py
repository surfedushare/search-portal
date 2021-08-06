from rest_framework import generics
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from datagrowth.datatypes.views import DocumentBaseSerializer
from core.models import Extension, Document

from project.serializers import PersonSerializer, OrganisationSerializer, ProjectSerializer


class ExtensionSerializer(DocumentBaseSerializer):

    id = serializers.CharField(read_only=True)
    external_id = serializers.CharField(write_only=True)

    authors = PersonSerializer(many=True, write_only=True)
    parties = OrganisationSerializer(many=True, write_only=True)
    projects = ProjectSerializer(many=True, write_only=True)

    parents = serializers.ListField(child=serializers.CharField(), write_only=True)
    children = serializers.ListField(child=serializers.CharField(), write_only=True)

    def validate_relation_ids(self, ids):
        if not len(ids):
            return
        document_ids = {
            external_id
            for external_id in Document.objects.filter(reference__in=ids).values_list("reference", flat=True)
        }
        extension_ids = {
            external_id for external_id in Extension.objects.filter(id__in=ids).values_list("id", flat=True)
        }
        for external_id in ids:
            if external_id not in document_ids and external_id not in extension_ids:
                raise ValidationError(f"Document or Extension with id '{external_id}' does not exist.")

    def validate_parents(self, parents):
        self.validate_relation_ids(parents)
        return parents

    def validate_children(self, children):
        self.validate_relation_ids(children)
        return children

    def validate(self, attrs):
        external_id = attrs["external_id"]
        if not attrs.get("is_parent", False):
            if not Document.objects.filter(reference=external_id).exists():
                raise ValidationError(
                    f"Could not find Document with external_id '{external_id}'. Did you mean to create a parent?"
                )
        if self.context["request"].method == "POST":
            if Extension.objects.filter(id=external_id).exists():
                raise ValidationError(
                    f"Extension with id '{external_id}' already exists. Try to PUT the extension instead."
                )
        return super().validate(attrs)

    def create(self, validated_data):
        external_id = validated_data["external_id"]
        is_parent = validated_data.pop("is_parent")
        return super().create({
            "id": external_id,
            "reference": external_id,
            "is_parent": is_parent,
            "properties": validated_data
        })

    def update(self, instance, validated_data):
        validated_data.pop("external_id")
        validated_data.pop("is_parent", None)
        instance.properties.update(validated_data)
        instance.save()
        return super().update(instance, validated_data)

    class Meta:
        model = Extension
        fields = ("id", "created_at", "modified_at", "properties", "is_parent", "external_id", "authors", "parties",
                  "projects", "parents", "children")


class ExtensionListView(generics.ListCreateAPIView):
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer


class ExtensionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer

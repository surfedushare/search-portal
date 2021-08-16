from django.conf import settings
from rest_framework import generics
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from datagrowth.datatypes.views import DocumentBaseSerializer
from core.models import Extension, Document

from project.serializers import PersonSerializer, OrganisationSerializer, ProjectSerializer, LabelSerializer


class ExtensionSerializer(DocumentBaseSerializer):

    id = serializers.CharField(read_only=True)
    external_id = serializers.CharField(write_only=True)
    is_parent = serializers.BooleanField(required=False, default=False)

    title = serializers.CharField(write_only=True, required=False)
    description = serializers.CharField(write_only=True, required=False)
    language = serializers.CharField(write_only=True, required=False, max_length=2)
    published_at = serializers.DateField(write_only=True, required=False)
    copyright = serializers.ChoiceField(write_only=True, required=False, choices=settings.COPYRIGHT_VALUES)

    authors = PersonSerializer(many=True, write_only=True, required=False)
    parties = OrganisationSerializer(many=True, write_only=True, required=False)
    projects = ProjectSerializer(many=True, write_only=True, required=False)
    themes = LabelSerializer(many=True, write_only=True, required=False)
    keywords = LabelSerializer(many=True, write_only=True, required=False)

    parents = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    children = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    def validate_external_id(self, external_id):
        path_external_id = self.context["view"].kwargs.get("pk")
        if path_external_id and path_external_id != external_id:
            raise ValidationError("External id in path and body do not match.")
        return external_id

    def validate_published_at(self, published_at):
        return published_at.strftime("%Y-%m-%d")

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
            parental_properties = ["title", "description", "language", "published_at", "copyright"]
            for prop in parental_properties:
                if prop in attrs:
                    raise ValidationError(
                        f"Can't set {prop} property for anything but a parent extension."
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
            "is_parent": is_parent,
            "reference": external_id,
            "properties": validated_data
        })

    def update(self, instance, validated_data):
        validated_data.pop("is_parent", None)
        instance.properties.update(validated_data)
        instance.save()
        return super().update(instance, validated_data)

    class Meta:
        model = Extension
        fields = ("id", "created_at", "modified_at", "properties", "is_parent", "external_id",
                  "title", "description", "language", "published_at", "copyright",
                  "authors", "parties", "projects", "themes", "keywords", "parents", "children")


class ExtensionListView(generics.ListCreateAPIView):
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer


class ExtensionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer

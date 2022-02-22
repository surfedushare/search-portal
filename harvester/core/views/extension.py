from django.conf import settings
from django.utils.timezone import now
from rest_framework import generics
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from datagrowth.datatypes.views import DocumentBaseSerializer
from harvester.schema import HarvesterSchema
from core.models import Extension, Document

from project.serializers import PersonSerializer, OrganisationSerializer, ProjectSerializer, LabelSerializer


class ExtensionPropertiesSerializer(serializers.Serializer):

    external_id = serializers.CharField()
    state = serializers.ChoiceField(required=False, choices=Document.States.choices)
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    language = serializers.CharField(required=False, max_length=2)
    published_at = serializers.DateField(required=False)
    copyright = serializers.ChoiceField(required=False, choices=settings.COPYRIGHT_VALUES)

    authors = PersonSerializer(many=True, required=False)
    parties = OrganisationSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    themes = LabelSerializer(many=True, required=False)
    keywords = LabelSerializer(many=True, required=False)

    parents = serializers.ListField(child=serializers.CharField(), required=False)
    children = serializers.ListField(child=serializers.CharField(), required=False)


class ExtensionSerializer(DocumentBaseSerializer, ExtensionPropertiesSerializer):

    id = serializers.CharField(read_only=True)
    is_addition = serializers.BooleanField(required=False, default=False)
    properties = ExtensionPropertiesSerializer(read_only=True)

    external_id = serializers.CharField(write_only=True)
    state = serializers.CharField(write_only=True, required=False)
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
        path_external_id = self.context["view"].kwargs.get("external_id")
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
        if not attrs.get("is_addition", False):
            if not Document.objects.filter(reference=external_id).exists():
                raise ValidationError(
                    f"Could not find Document with external_id '{external_id}'. Did you mean to create an addition?"
                )
            addition_properties = ["language", "published_at", "copyright"]
            for prop in addition_properties:
                if prop in attrs:
                    raise ValidationError(
                        f"Can't set {prop} property for anything but an addition extension."
                    )
        if self.context["request"].method == "POST":
            if Extension.objects.filter(id=external_id).exists():
                raise ValidationError(
                    f"Extension with id '{external_id}' already exists. Try to PUT the extension instead."
                )
        return super().validate(attrs)

    def create(self, validated_data):
        external_id = validated_data["external_id"]
        is_addition = validated_data.pop("is_addition")
        extension = super().create({
            "id": external_id,
            "is_addition": is_addition,
            "reference": external_id,
            "properties": validated_data
        })
        if not is_addition:
            Document.objects.filter(reference=external_id).update(modified_at=now(), extension=extension)
        return extension

    def update(self, instance, validated_data):
        is_addition = validated_data.pop("is_addition", None)
        if not is_addition:
            Document.objects.filter(reference=validated_data["external_id"]).update(modified_at=now())
        instance.properties.update(validated_data)
        instance.save()
        return super().update(instance, validated_data)

    class Meta:
        model = Extension
        fields = ("id", "created_at", "modified_at", "properties", "is_addition", "external_id", "state",
                  "title", "description", "language", "published_at", "copyright",
                  "authors", "parties", "projects", "themes", "keywords", "parents", "children")


class ExtensionListView(generics.ListCreateAPIView):
    """
    Returns a list of all existing extensions (GET) and allows for adding new extensions (POST).

    An extension is a way for anybody to enrich the data that is coming from repositories.
    When documents from repositories get indexed by the search engine
    the properties of an extension will overwrite the values from repository documents,
    except for the "children" and "parents" properties.
    Those lists get concatenated with the values from repository documents.

    ## Request body

    To create an extension it should get posted to this endpoint.
    Below is a list of properties that you can set on an extension.
    When performing a GET the same properties can be read.

    **external_id**: The identifier of the document that this extension extends.
    These identifiers are provided by the repository that provided the metadata.
    When is_addition is true you must provide your own unique identifier.

    **is_addition**: Sometimes a document does not exist in any source system.
    is_addition should be true if you want to create an extension that doesn't refer to any document in source systems.
    Since there exists no repository document for this type of extension,
    the external_id must be set by its creator upon a POST.
    The values of the title, description, language, published_at and copyright properties (if given)
    will be used as data to search through.

    **authors**: (optional) The list of authors that this extension should overwrite.
    An author consists of a name and email address.

    **parties**: (optional) A list of organizations or agents that this extension should add to the search data.
    A party consists of a name.

    **projects**: (optional) A list of projects that this extension should adds to the search data.
    A project consists of a name.

    **themes**: (optional) A list of themes that this extension should overwrite.
    A theme Consists of a label.

    **keywords**: (optional) A list of keywords that this extension should overwrite.
    A keyword consists of a label.

    **parents**: (optional) A list of external_id identifiers that will be added as parents by the extension.

    **childs**: (optional) A list of external_id identifiers that will be added as children by the extension.

    ## Response body

    The response contains a list of extensions (GET) or the newly created extension (POST).
    See request body to learn more about the properties of an extension.
    """
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer
    schema = HarvesterSchema()


class ExtensionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    This endpoint allows you to retrieve, update or delete an extension.

    An extension is a way for anybody to enrich the data that is coming from repositories.
    When documents from repositories get indexed by the search engine
    the properties of an extension will overwrite the values from repository documents,
    except for the "children" and "parents" properties.
    Those lists get concatenated with the values from repository documents.

    ## Request body

    To update an extension you should PUT it to this endpoint.
    Below is a list of properties that you can set on an extension.
    When performing a GET the same properties can be read.

    **external_id**: The identifier of the document that this extension extends.
    These identifiers are provided by the repository that provided the metadata or when is_addition is true
    by the creator of the extension.

    **is_addition**: Sometimes a document does not exist in any source system and gets added through an extension.
    is_addition will be true for such an extension. It is not possible to alter the is_addition property after creation.
    The values of the title, description, language, published_at and copyright properties (if given)
    will be used as data to search through. You can update these properties.

    **authors**: (optional) The list of authors that this extension should overwrite.
    An author consists of a name and email address.

    **parties**: (optional) A list of organizations or agents that this extension should add to the search data.
    A party consists of a name.

    **projects**: (optional) A list of projects that this extension should adds to the search data.
    A project consists of a name.

    **themes**: (optional) A list of themes that this extension should overwrite.
    A theme Consists of a label.

    **keywords**: (optional) A list of keywords that this extension should overwrite.
    A keyword consists of a label.

    **parents**: (optional) A list of external_id identifiers that will be added as parents by the extension.

    **childs**: (optional) A list of external_id identifiers that will be added as children by the extension.

    ## Response body

    The response contains an extension (GET or PUT) or an empty response (DELETE).
    See request body to learn more about the properties of an extension.
    """
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer
    lookup_url_kwarg = "external_id"
    schema = HarvesterSchema()

    def destroy(self, request, *args, **kwargs):
        Document.objects.filter(reference=kwargs["external_id"]).update(modified_at=now())
        return super().destroy(request, *args, **kwargs)

from rest_framework import generics
from rest_framework import serializers

from datagrowth.datatypes.views import ContentView, ContentSerializer, DocumentBaseSerializer
from core.models import Document


class DocumentSerializer(DocumentBaseSerializer):

    harvest_source = serializers.CharField(source="collection.name")
    feed = serializers.CharField(source="collection.name")
    properties = serializers.SerializerMethodField()

    def get_properties(self, document):
        properties = document.properties
        properties["owners"] = [next(iter(properties["authors"]), None)]
        properties["contacts"] = [next(iter(properties["authors"]), None)]
        return properties

    class Meta:
        model = Document
        fields = DocumentBaseSerializer.default_fields + ("harvest_source", "feed",)


class MetadataDocumentSerializer(DocumentBaseSerializer):

    language = serializers.CharField(source="properties.language.metadata")

    class Meta:
        model = Document
        fields = ("id", "reference", "language", "created_at", "modified_at")


class DocumentView(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentContentView(ContentView):
    queryset = Document.objects.all()
    serializer_class = ContentSerializer
    content_class = Document

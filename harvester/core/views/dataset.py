from rest_framework import generics

from datagrowth.datatypes.views import CollectionBaseSerializer, CollectionBaseContentView
from core.models import Document, Dataset, ElasticIndexSerializer
from core.views.document import DocumentSerializer


class DatasetDetailSerializer(CollectionBaseSerializer):

    content = DocumentSerializer(many=True, source="documents")

    class Meta:
        model = Dataset
        fields = CollectionBaseSerializer.default_fields + ("content", "annotations",)


class DatasetListSerializer(CollectionBaseSerializer):

    indices = ElasticIndexSerializer(many=True)

    class Meta:
        model = Dataset
        fields = CollectionBaseSerializer.default_fields + ("indices",)


class DatasetListView(generics.ListAPIView):
    queryset = Dataset.objects.all()
    serializer_class = DatasetListSerializer


class DatasetDetailView(generics.RetrieveAPIView):
    queryset = Dataset.objects.all()
    serializer_class = DatasetDetailSerializer


class DatasetContentView(CollectionBaseContentView):
    queryset = Dataset.objects.all()
    content_class = Document

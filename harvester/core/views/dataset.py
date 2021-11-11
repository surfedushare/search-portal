from django.shortcuts import Http404
from rest_framework import generics
from rest_framework.response import Response

from datagrowth.datatypes.views import CollectionBaseSerializer
from harvester.pagination import HarvesterPageNumberPagination
from harvester.schema import HarvesterSchema
from core.models import Dataset
from core.views.document import DocumentSerializer, MetadataDocumentSerializer


class DatasetDetailSerializer(CollectionBaseSerializer):

    class Meta:
        model = Dataset
        fields = CollectionBaseSerializer.default_fields


class DatasetListSerializer(CollectionBaseSerializer):

    class Meta:
        model = Dataset
        fields = CollectionBaseSerializer.default_fields


class DatasetListView(generics.ListAPIView):
    """
    Returns a list of all available Datasets.
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetListSerializer
    schema = HarvesterSchema()


class DatasetDetailView(generics.RetrieveAPIView):
    """
    Returns the metadata for a dataset.
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetDetailSerializer
    schema = HarvesterSchema()


class DatasetDocumentsView(generics.ListAPIView):
    """
    Returns a list of documents that are part of a dataset.
    Within a single Dataset the schema of the JSON objects for documents is consistent.
    However within different datasets the schema may change and thus the exact schema is not documented.
    """
    pagination_class = HarvesterPageNumberPagination
    queryset = Dataset.objects.all()
    serializer_class = DocumentSerializer
    schema = HarvesterSchema()

    def list(self, request, *args, **kwargs):
        try:
            dataset = self.get_object()
        except Http404:
            if kwargs["pk"] is not None:
                raise Http404("Not found")
            dataset = Dataset.objects.filter(is_latest=True).last()
        if dataset is None:
            raise Http404("No content found")

        dataset_version = dataset.versions.get_latest_version()
        page = self.paginate_queryset(dataset_version.document_set.all())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(dataset_version.document_set.iterator(), many=True)
        return Response({
            "count": dataset_version.document_set.count(),
            "next": None,
            "previous": None,
            "results": serializer.data
        })


class DatasetMetadataDocumentsView(DatasetDocumentsView):
    serializer_class = MetadataDocumentSerializer

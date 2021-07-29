"""
This module contains implementation of REST API views for stats app.
"""
from rest_framework import generics
from rest_framework import serializers
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from surf.vendor.elasticsearch.api import ElasticSearchApiClient
from surf.apps.core.schema import SearchSchema


class StatsViewSet(ViewSet):
    """
    View class that provides statistics information.
    """

    permission_classes = []

    @action(methods=['get'], url_path="all-materials", detail=False)
    def all_materials(self, request, **kwargs):
        """
        Returns the number of all available materials
        """
        elastic = ElasticSearchApiClient()
        return Response(dict(value=elastic.stats()))


class StatsSerializer(serializers.Serializer):

    documents = serializers.IntegerField()


class StatsView(generics.RetrieveAPIView):
    """
    This endpoint gives information about the indices in the search engine.
    You can think of an index as a database table,
    but instead of rows there are documents, which are optimized for search.

    ## Response body

    **documents**: The sum of documents present in all indices

    """

    permission_classes = []
    serializer_class = StatsSerializer
    schema = SearchSchema()
    pagination_class = None
    filter_backends = []

    def get_object(self):
        elastic = ElasticSearchApiClient()
        return {
            "documents": elastic.stats()
        }

from django.conf import settings
from rest_framework import generics
from rest_framework import serializers
from rest_framework.permissions import AllowAny

from harvester.schema import HarvesterSchema
from search.clients import get_search_client


class StatsSerializer(serializers.Serializer):

    documents = serializers.IntegerField()


class SearchStatsAPIView(generics.RetrieveAPIView):
    """
    This endpoint gives information about the documents in the search engine.

    You can think of a search engine as a database table,
    but instead of rows there are "documents", which are optimized for search.

    ## Response body

    **documents**: The sum of documents present in Open Search

    """
    document_type = settings.DOCUMENT_TYPE
    permission_classes = (AllowAny,)
    serializer_class = StatsSerializer
    schema = HarvesterSchema()

    def get_object(self):
        client = get_search_client(self.document_type)
        return {
            "documents": client.stats()
        }

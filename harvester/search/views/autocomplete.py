from django.conf import settings
from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from harvester.schema import HarvesterSchema
from search.clients import get_search_client


class AutocompleteRequestSerializer(serializers.Serializer):
    query = serializers.CharField(write_only=True)


class AutocompleteAPIView(generics.GenericAPIView):
    """
    This endpoint returns suggestions about what a user may be typing.
    Call this endpoint when a user is typing a search and display the results (for instance below the search bar).
    """
    document_type = settings.DOCUMENT_TYPE
    serializer_class = AutocompleteRequestSerializer
    permission_classes = (AllowAny,)
    schema = HarvesterSchema()
    pagination_class = None

    def get(self, request, *args, **kwargs):
        # validate request parameters
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        client = get_search_client(self.document_type)
        response = client.autocomplete(**data)
        return Response(response)

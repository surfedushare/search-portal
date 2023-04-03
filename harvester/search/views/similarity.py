from django.conf import settings
from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from search_client import DocumentTypes
from search_client.serializers import LearningMaterialResultSerializer, ResearchProductResultSerializer
from search.clients import get_search_client
from harvester.schema import HarvesterSchema


class SimilaritySerializer(serializers.Serializer):
    external_id = serializers.CharField(write_only=True, required=True)
    language = serializers.CharField(write_only=True, required=True)


class LearningMaterialSimilaritySerializer(SimilaritySerializer):
    results = LearningMaterialResultSerializer(many=True, read_only=True)
    results_total = serializers.IntegerField(read_only=True)


class ResearchProductSimilaritySerializer(SimilaritySerializer):
    results = ResearchProductResultSerializer(many=True, read_only=True)
    results_total = serializers.IntegerField(read_only=True)


class AuthorSuggestionSerializer(serializers.Serializer):
    author_name = serializers.CharField(write_only=True, required=True)


class LearningMaterialAuthorSuggestionSerializer(AuthorSuggestionSerializer):
    results = LearningMaterialResultSerializer(many=True, read_only=True)
    results_total = serializers.IntegerField(read_only=True)


class ResearchProductAuthorSuggestionSerializer(AuthorSuggestionSerializer):
    results = ResearchProductResultSerializer(many=True, read_only=True)
    results_total = serializers.IntegerField(read_only=True)


class SimilarityAPIView(GenericAPIView):
    """
    This endpoint returns similar documents as the input document.
    These similar documents can be offered as suggestions to look at for the user.
    """
    document_type = settings.DOCUMENT_TYPE
    permission_classes = (AllowAny,)
    schema = HarvesterSchema()

    def get_serializer_class(self):
        if self.document_type == DocumentTypes.LEARNING_MATERIAL:
            return LearningMaterialSimilaritySerializer
        elif self.document_type == DocumentTypes.RESEARCH_PRODUCT:
            return ResearchProductSimilaritySerializer
        else:
            raise AssertionError("SimilarityAPIView expected application to use different DOCUMENT_TYPE")

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        external_id = serializer.validated_data["external_id"]
        language = serializer.validated_data["language"]
        client = get_search_client(self.document_type)
        results = client.more_like_this(external_id, language)
        results.pop("records_total", None)
        return Response(results)


class AuthorSuggestionsAPIView(GenericAPIView):
    """
    This endpoint returns documents where the name of the author appears in the text or metadata,
    but is not set as author in the authors field.
    These documents can be offered to authors as suggestions for more content from their hand.
    """
    document_type = settings.DOCUMENT_TYPE
    permission_classes = (AllowAny,)
    schema = HarvesterSchema()

    def get_serializer_class(self):
        if self.document_type == DocumentTypes.LEARNING_MATERIAL:
            return LearningMaterialAuthorSuggestionSerializer
        elif self.document_type == DocumentTypes.RESEARCH_PRODUCT:
            return ResearchProductAuthorSuggestionSerializer
        else:
            raise AssertionError("AuthorSuggestionsAPIView expected application to use different DOCUMENT_TYPE")

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        author_name = serializer.validated_data["author_name"]
        client = get_search_client(self.document_type)
        results = client.author_suggestions(author_name)
        results.pop("records_total", None)
        return Response(results)

from django.conf import settings
from django.core.validators import MinValueValidator
from django.shortcuts import Http404
from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from search_client import DocumentTypes
from search_client.serializers import LearningMaterialResultSerializer, ResearchProductResultSerializer
from harvester.schema import HarvesterSchema
from metadata.models import MetadataField
from search.clients import get_search_client


class DocumentSearchFilterSerializer(serializers.Serializer):

    external_id = serializers.CharField()
    items = serializers.ListField(child=serializers.CharField(allow_null=True))


class DocumentSearchSerializer(serializers.Serializer):

    search_text = serializers.CharField(required=True, allow_blank=True, write_only=True)
    filters = DocumentSearchFilterSerializer(many=True, write_only=True, default=[])

    page = serializers.IntegerField(required=False, default=1, validators=[MinValueValidator(1)])
    page_size = serializers.IntegerField(required=False, default=10, validators=[MinValueValidator(0)])

    results_total = serializers.DictField(read_only=True)

    def validate_filters(self, filters):
        filter_fields = self.context.get("filter_fields", None)
        if not filter_fields:
            return filters
        for metadata_filter in filters:
            field_id = metadata_filter.get("external_id", None)
            if field_id not in filter_fields:
                raise ValidationError(detail=f"Invalid external_id for metadata field in filter '{field_id}'")


class LearningMaterialSearchSerializer(DocumentSearchSerializer):
    results = LearningMaterialResultSerializer(many=True, read_only=True)


class ResearchProductSearchSerializer(DocumentSearchSerializer):
    results = ResearchProductResultSerializer(many=True, read_only=True)


class DocumentSearchAPIView(GenericAPIView):
    """
    The main search endpoint.
    Specify the search query in the **search_text** property of the body to do a simple search.
    All other properties are optional and are described below

    ## Request body

    Apart from search_text you can specify the following properties in the body of the request:

    **page_size**: Number of results to return per page.

    **page**: A page number within the paginated result set.

    **filters**: Filters consist of an array of objects that specify an external_id and an items property.
    The external_id should be the value of a "field" filter category (for instance: "technical_type").
    See the filter categories endpoint described below for more details on filter categories.
    Next to the external_id you should specify an array under the items property.
    Elements in this array should only consist of values from category filter objects (for instance: "video").

    Filters under the same "field" filter category will function as an OR filter.
    While multiple filter category items across "field" filter categories function as AND filters.

    ## Response body

    **results**: An array containing the search results.

    **results_total**: Object with information about the total amount of found documents.
    The "value" key gives the found documents count. The "is_precise" key is true when the value is exact
    or false when it indicates the lower bound.

    **page_size**: Number of results to return per page.

    **page**: The current page number.

    """
    document_type = settings.DOCUMENT_TYPE
    permission_classes = (AllowAny,)
    schema = HarvesterSchema()

    def get_serializer_class(self):
        if self.document_type == DocumentTypes.LEARNING_MATERIAL:
            return LearningMaterialSearchSerializer
        elif self.document_type == DocumentTypes.RESEARCH_PRODUCT:
            return ResearchProductSearchSerializer
        else:
            raise AssertionError("DocumentSearchAPIView expected application to use different DOCUMENT_TYPE")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["filter_fields"] = MetadataField.objects.exclude(is_manual=True).values_list("name", flat=True)
        return context

    def post(self, request, *args, **kwargs):
        # Validate request parameters and prepare search
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        include_filter_counts = request.GET.get("include_filter_counts", None)
        if include_filter_counts == "1":
            data["drilldown_names"] = serializer.context["filter_fields"]
        # Execute search and return results
        client = get_search_client(self.document_type)
        response = client.search(**data)
        return Response({
            "results": response["results"],
            "results_total": response["results_total"],
            "did_you_mean": response["did_you_mean"],
            "page": data["page"],
            "page_size": data["page_size"],
            "filter_counts": response["drilldowns"] if include_filter_counts == "1" else None
        })


class DocumentSearchDetailAPIView(GenericAPIView):
    """
    Searches for a document with the specified external_id.
    It raises a 404 if the document is not found.
    Otherwise it returns the document as an object.
    """

    document_type = settings.DOCUMENT_TYPE
    permission_classes = (AllowAny,)
    schema = HarvesterSchema()

    def get_serializer_class(self):
        if self.document_type == DocumentTypes.LEARNING_MATERIAL:
            return LearningMaterialResultSerializer
        elif self.document_type == DocumentTypes.RESEARCH_PRODUCT:
            return ResearchProductResultSerializer
        else:
            raise AssertionError("DocumentSearchDetailAPIView expected application to use different DOCUMENT_TYPE")

    def get_object(self):
        client = get_search_client(self.document_type)
        response = client.get_documents_by_id([self.kwargs["external_id"]])
        records = response.get("results", [])
        if not records:
            raise Http404()
        document = records[0]
        return document

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance)


class LearningMaterialDetailsSerializer(serializers.Serializer):
    external_ids = serializers.ListField(child=serializers.CharField(), write_only=True)
    results = LearningMaterialResultSerializer(many=True, read_only=True)
    records_total = serializers.IntegerField(read_only=True)


class ResearchProductDetailsSerializer(serializers.Serializer):
    external_ids = serializers.ListField(child=serializers.CharField(), write_only=True)
    results = ResearchProductResultSerializer(many=True, read_only=True)
    records_total = serializers.IntegerField(read_only=True)


class DocumentSearchDetailsAPIView(GenericAPIView):
    """
    Searches for documents with the specified external ids.

    ## Request body

    **external_ids**: A list of external ids to find documents for

    ## Response body

    **results**: The list of documents that match the external ids

    **results_total**: Object with information about the total amount of found documents.
    The "value" key gives the found documents count. This could be less than the amount of given external ids
    if some of the external ids weren't found. The "is_precise" key is true when the value is exact
    or false when it indicates the lower bound.
    """

    document_type = settings.DOCUMENT_TYPE
    permission_classes = (AllowAny,)
    schema = HarvesterSchema()
    max_page_size = 100

    def get_serializer_class(self):
        if self.document_type == DocumentTypes.LEARNING_MATERIAL:
            return LearningMaterialDetailsSerializer
        elif self.document_type == DocumentTypes.RESEARCH_PRODUCT:
            return ResearchProductDetailsSerializer
        else:
            raise AssertionError("DocumentSearchDetailAPIView expected application to use different DOCUMENT_TYPE")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        external_ids = serializer.validated_data["external_ids"]
        if len(external_ids) > self.max_page_size:
            raise ValidationError(detail=f"Can't process more than {self.max_page_size} external ids at a time")
        client = get_search_client(self.document_type)
        response = client.get_documents_by_id(external_ids, page_size=self.max_page_size)
        results = response.get("results", [])
        return Response({
            "results": results,
            "results_total": {
                "value": len(results),
                "is_precise": True
            }
        })

from django.views.decorators.gzip import gzip_page
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from harvester.schema import HarvesterSchema
from metadata.models import MetadataField, MetadataFieldSerializer, MetadataValue, MetadataValueSerializer


@method_decorator(gzip_page, name="dispatch")
class MetadataTreeView(generics.ListAPIView):
    """
    The metadata tree is used for filtering with the full text search endpoint.
    This endpoint returns all available metadata values.

    There are two types of nodes in the metadata tree.
    The root metadata nodes have a **field** value of null.
    These nodes are all returned in the main array of the response and they represent fields that you can filter on.

    Other nodes are returned as the children of the "field" nodes. The values of these nodes can be filtered on.
    Typically you'll send the value of a "field" node
    together with a number of values from nodes you want to filter on to the search endpoint.

    When filtering take note that if somebody selects a non-field node that has children,
    then you'll want to send the values of these children together with the value of the parent
    as filter values in the search request. Failing to do this will yield unexpected results.

    ## Response body

    The response contains a list of metadata nodes. Each metadata node contains the following properties:

    **field**: The metadata field this node belongs to or null if the node is itself a metadata field.

    **parent**: The id of a parent node or null.

    **translation**: The translated display name of the metadata. Formerly the title_translations.

    **value**: Use this value to filter in the search endpoint. Formerly the external_id

    **is_hidden**: Whether this node should be visible for users.

    **children**: All nodes that have this node as a parent.

    **children_count**: Total number of children.
    When the max_children parameter is used this property will still reflect the true available amount of children.

    **frequency**: How many results match this node in the entire dataset.

    """
    queryset = MetadataField.objects.filter(is_hidden=False).select_related("translation")
    serializer_class = MetadataFieldSerializer
    schema = HarvesterSchema()
    pagination_class = None


@method_decorator(gzip_page, name="dispatch")
class MetadataFieldValuesView(generics.ListAPIView):

    queryset = MetadataValue.objects.filter(deleted_at__isnull=True)
    serializer_class = MetadataValueSerializer
    schema = HarvesterSchema()
    pagination_class = PageNumberPagination

    def filter_queryset(self, queryset):
        site_id = self.request.GET.get("site_id", 1)
        queryset = queryset.filter(field__name=self.kwargs["field"], site__id=site_id)
        startswith = self.kwargs.get("startswith", None)
        if startswith:
            queryset = queryset.filter(value__istartswith=startswith)
        return queryset

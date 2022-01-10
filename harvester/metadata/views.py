from django.views.decorators.gzip import gzip_page
from django.utils.decorators import method_decorator
from rest_framework import generics

from harvester.schema import HarvesterSchema
from metadata.models import MetadataField, MetadataFieldSerializer


@method_decorator(gzip_page, name="dispatch")
class MetadataTreeView(generics.ListAPIView):
    """
    The metadata tree is used for filtering with the full text search endpoint (part of the search service).
    This endpoint returns all available metadata values.
    Usually a call to the search endpoint is all you need
    as that will also return all metadata values as "filter categories",
    but here we'll explain about the metadata structure in a bit more detail.

    There are two types of nodes in the metadata tree.
    The root metadata nodes do not have a parent.
    These nodes are all returned in the main array of the response and they represent fields that you can filter on.

    Other nodes are returned as the children of the "field" nodes. The values of these nodes can be filtered on.
    Typically you'll send the value of a "field" node
    together with a number of values from nodes you want to filter on to the search endpoint.

    When filtering take note that if somebody selects a non-field node that has children,
    then you'll want to send the values of these children together with the value of the parent
    as filter values in the search request. Failing to do this will yield unexpected results.

    ## Response body

    The response contains a list of metadata nodes. Each metadata node contains the following properties:

    **parent**: The id of a parent node or null.
    Mainly useful to detect if a node is a "field" node or not.

    **translation**: The translated display name of the metadata. Formerly the title_translations.

    **value**: Use this value to filter in the search endpoint. Formerly the external_id

    **is_hidden**: Whether this node should be visible for users.

    **children**: All nodes that have this node as a parent.

    **frequency**: How many results match this node last time it was checked. Formerly the "count"

    """
    queryset = MetadataField.objects.select_related("translation")
    serializer_class = MetadataFieldSerializer
    schema = HarvesterSchema()
    pagination_class = None

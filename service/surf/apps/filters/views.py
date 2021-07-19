"""
This module contains implementation of REST API views for filters app.
"""

from rest_framework import generics

from surf.apps.core.schema import SearchSchema
from surf.apps.filters.models import MpttFilterItem
from surf.apps.filters.serializers import MpttFilterItemSerializer


class FilterCategoryView(generics.ListAPIView):
    """
    Filter categories are used for filtering in the search endpoint (see the search endpoint above).
    This endpoint returns all available filter categories.
    Usually a call to the search endpoint is all you need as that will also return all filter categories,
    but here we'll explain about filter categories in a bit more detail.

    There are two types of filter categories. The "root" filter categories do not have a parent filter category.
    These filter categories are all returned in the main array of the response.
    Other filter categories have a root filter category as parent or another filter category.
    These filter categories are returned as the "children" of the parent filter categories.
    When filtering take note that if somebody selects a non-root filter category that has children,
    then you'll want to send the external_id of these children together with the external_id of the parent
    as items in the search request. Failing to do this will yield unexpected results.

    ## Response body

    The response contains a list of filter categories. Each filter category contains the following properties:

    **name**: Human readable name of the filter category. Can act as a backup when translations are missing.

    **parent**: The id of a parent filter category or null.
    Mainly useful to detect if a filter category is a root filter category or not.

    **title_translations**: The translated name of the filter category.

    **external_id**: Use this value to filter in the search endpoint (described above).

    **is_hidden**: Whether this filter category should be visible for users.

    **children**: All filter categories that have this filter category as a parent.

    **count**: How many results match this filter category or 0 when no search is executed.

    """
    serializer_class = MpttFilterItemSerializer
    permission_classes = []
    schema = SearchSchema()
    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        return MpttFilterItem.objects.select_related("title_translations").get_cached_trees()


class MpttFilterItems(generics.GenericAPIView):
    serializer_class = MpttFilterItemSerializer

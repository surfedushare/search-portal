from django.apps import apps
from django.views.decorators.gzip import gzip_page
from django.utils.decorators import method_decorator
from rest_framework import generics

from surf.apps.core.schema import SearchSchema
from surf.apps.filters.serializers import MpttFilterItemSerializer


filters_app = apps.get_app_config("filters")


@method_decorator(gzip_page, name="dispatch")
class FilterCategoryView(generics.ListAPIView):
    """
    Filter categories are used for filtering in the search endpoint (see the search endpoint above).
    This endpoint returns all available filter categories.
    Usually a call to the search endpoint is all you need as that will also return all filter categories,
    but here we'll explain about filter categories in a bit more detail.

    There are two types of filter categories. The "field" filter categories have a field property of null.
    These filter categories are all returned in the main array of the response.
    Regular filter categories do have a field property set.
    These filter categories may have a parent, which is another regular filter category
    and never a "field" filter category.

    Filter categories that have a parent set will be returned as the "children" of the parent filter categories.
    "Field" filter categories also have children which will be all regular filter categories that specify that field
    and which do not specify a parent (the ones that specify a parent are returned as child of that parent instead).

    When filtering take note that if somebody selects a filter category that has children,
    then you'll want to send the value of these children together with the value of the parent
    as items in the search request. Failing to do this will yield unexpected results.

    ## Response body

    The response contains a list of filter categories. Each filter category contains the following properties:

    **field**: The value of a filter category that describes the filter field of the filter category
    (will be null for "field" filter categories)

    **parent**: The id of a parent filter category or null.

    **translation**: The translated names of the filter category.

    **value**: Use this value to filter in the search endpoint (described above).

    **external_id**: Deprecated, use "value" instead

    **is_hidden**: Whether this filter category should be visible for users.

    **children**: All filter categories that have this filter category as a parent.

    **frequency**: How many results match this filter category or 0 when no search is executed.

    """
    serializer_class = MpttFilterItemSerializer
    permission_classes = []
    schema = SearchSchema()
    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        return filters_app.metadata.tree

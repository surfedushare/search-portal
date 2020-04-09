"""
This module contains implementation of core mixins.
"""

from rest_framework.response import Response
from rest_framework import status


class ListDestroyModelMixin(object):
    """
    Destroy list of instances.
    """

    def list_destroy(self, request, *args, **kwargs):
        self.filter_queryset(self.get_queryset()).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

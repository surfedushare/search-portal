"""
This module contains implementation of core pagination classes.
"""

from rest_framework.pagination import PageNumberPagination


class SurfPageNumberPagination(PageNumberPagination):
    """
    Overwrites PageNumberPagination class and adds page_size query parameter.
    """
    page_size_query_param = "page_size"

from rest_framework.pagination import PageNumberPagination


class HarvesterPageNumberPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = "page_size"

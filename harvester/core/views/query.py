from rest_framework import viewsets, mixins, permissions

from core.models.search import Query, QuerySerializer


class QueryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):

    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [permissions.IsAuthenticated]

from rest_framework import generics

from datagrowth.datatypes.views import CollectionBaseSerializer, CollectionBaseContentView
from core.models import Arrangement, Document
from core.views.document import DocumentSerializer


class ArrangementSerializer(CollectionBaseSerializer):

    content = DocumentSerializer(many=True, source="documents")

    class Meta:
        model = Arrangement
        fields = CollectionBaseSerializer.default_fields + ("content",)


class ArrangementView(generics.RetrieveAPIView):
    queryset = Arrangement.objects.all()
    serializer_class = ArrangementSerializer


class ArrangementContentView(CollectionBaseContentView):
    queryset = Arrangement.objects.all()
    content_class = Document

from django.shortcuts import render, Http404
from rest_framework import generics

from datagrowth.datatypes.views import ContentView, ContentSerializer, DocumentBaseSerializer
from core.models import Document


class DocumentSerializer(DocumentBaseSerializer):

    class Meta:
        model = Document
        fields = DocumentBaseSerializer.default_fields


class DocumentView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentContentView(ContentView, generics.UpdateAPIView):
    queryset = Document.objects.all()
    serializer_class = ContentSerializer
    content_class = Document

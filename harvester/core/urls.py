from django.urls import path
from rest_framework import routers

from core import views


router = routers.SimpleRouter()
router.register("query", views.QueryViewSet)


app_name = 'core'
deprecated_api_patterns = [
    path('dataset/<int:pk>/documents/', views.DatasetDocumentsView.as_view(), name="dataset-documents"),
    path('dataset/<int:pk>/', views.DatasetDetailView.as_view(), name="dataset-detail"),
    path('dataset/', views.DatasetListView.as_view(), name="datasets"),
    path(
        'dataset/metadata-documents/', views.DatasetMetadataDocumentsView.as_view(),
        name="dataset-metadata-documents", kwargs={"pk": None}
    ),
]
public_api_patterns = [
    # Extensions
    path('extension/<str:external_id>/', views.ExtensionDetailView.as_view(), name="extension-detail"),
    path('extension/', views.ExtensionListView.as_view(), name="extensions"),
    # Documents
    path('document/raw/<str:external_id>/', views.RawDocumentDetailView.as_view(), name="raw-document-detail"),
    path('document/raw/', views.RawDocumentListView.as_view(), name="raw-documents"),
    path(
        'document/metadata/<str:external_id>/', views.MetadataDocumentDetailView.as_view(),
        name="metadata-document-detail"
    ),
    path('document/metadata/', views.MetadataDocumentListView.as_view(), name="metadata-documents"),
]
urlpatterns = public_api_patterns + router.urls + deprecated_api_patterns

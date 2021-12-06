from django.urls import path
from rest_framework import routers

from core import views


router = routers.SimpleRouter()
router.register("query", views.QueryViewSet)


app_name = 'core'
public_api_patterns = [
    path('dataset/metadata-documents/', views.DatasetMetadataDocumentsView.as_view(), name="dataset-metadata-documents",
         kwargs={"pk": None}),
    path('dataset/<int:pk>/documents/', views.DatasetDocumentsView.as_view(), name="dataset-documents"),
    path('dataset/<int:pk>/', views.DatasetDetailView.as_view(), name="dataset-detail"),
    path('dataset/', views.DatasetListView.as_view(), name="datasets"),
    path('extension/<str:external_id>/', views.ExtensionDetailView.as_view(), name="extension-detail"),
    path('extension/', views.ExtensionListView.as_view(), name="extensions"),
]
urlpatterns = public_api_patterns + router.urls

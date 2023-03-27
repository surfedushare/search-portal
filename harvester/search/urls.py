from django.urls import path

from search import views


app_name = 'search'
public_api_patterns = [
    path(r'search/documents', views.DocumentSearchAPIView.as_view(), name="search-documents"),
    path(
        r'search/documents/<str:external_id>', views.DocumentSearchDetailAPIView.as_view(),
        name="search-documents-detail"
    ),
]
urlpatterns = public_api_patterns

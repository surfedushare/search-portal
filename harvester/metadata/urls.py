from django.urls import path

from metadata import views


app_name = 'metadata'
public_api_patterns = [
    path('metadata/tree/', views.MetadataTreeView.as_view()),
    path('metadata/field-values/<str:field>/', views.MetadataFieldValuesView.as_view()),
    path('metadata/field-values/<str:field>/<str:startswith>/', views.MetadataFieldValuesView.as_view()),
]
urlpatterns = public_api_patterns

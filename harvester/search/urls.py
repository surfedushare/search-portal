from django.urls import path

from search import views


app_name = 'search'
public_api_patterns = [
    path(r'search/documents/', views.DocumentSearchAPIView.as_view(), name="search-documents"),
    path(r'search/autocomplete/', views.AutocompleteAPIView.as_view(), name="search-autocomplete"),
    path(r'search/stats/', views.SearchStatsAPIView.as_view(), name="search-stats"),
    path(r'find/documents/', views.DocumentSearchDetailsAPIView.as_view(), name="find-document-details"),
    path(
        r'find/documents/<str:external_id>/', views.DocumentSearchDetailAPIView.as_view(),
        name="find-document-detail"
    ),
    path(r'suggestions/similarity/', views.SimilarityAPIView.as_view()),
    path(r'suggestions/author/', views.AuthorSuggestionsAPIView.as_view()),
]
urlpatterns = public_api_patterns

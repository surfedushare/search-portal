from django.urls import path

from core import views


app_name = 'core'
urlpatterns = [
    path('document/<int:pk>/content/', views.DocumentContentView.as_view(), name="document-content"),
    path('document/<int:pk>/', views.DocumentView.as_view(), name="document"),
    path('collection/<int:pk>/content/', views.CollectionContentView.as_view(), name="collection-content"),
    path('collection/<int:pk>/', views.CollectionView.as_view(), name="collection"),
    path('dataset/<int:pk>/content/', views.DatasetContentView.as_view(), name="dataset-content"),
    path('dataset/<int:pk>/', views.DatasetDetailView.as_view(), name="dataset-detail"),
    path('datasets/', views.DatasetListView.as_view(), name="datasets"),
    path('extension/<str:pk>/', views.ExtensionDetailView.as_view(), name="extension-detail"),
    path('extension/', views.ExtensionListView.as_view(), name="extensions"),
]

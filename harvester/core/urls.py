from django.urls import path

from core import views


app_name = 'core'
urlpatterns = [
    path('document/<int:pk>/content/', views.DocumentContentView.as_view(), name="document-content"),
    path('document/<int:pk>/', views.DocumentView.as_view(), name="document"),
    path('arrangement/<int:pk>/content/', views.ArrangementContentView.as_view(), name="arrangement-content"),
    path('arrangement/<int:pk>/', views.ArrangementView.as_view(), name="arrangement"),
    path('collection/<int:pk>/content/', views.CollectionContentView.as_view(), name="collection-content"),
    path('collection/<int:pk>/', views.CollectionView.as_view(), name="collection"),
    path('dataset/<int:pk>/content/', views.DatasetContentView.as_view(), name="dataset-content"),
    path('dataset/<int:pk>/', views.DatasetDetailView.as_view(), name="dataset-detail"),
    path('datasets/', views.DatasetListView.as_view(), name="datasets"),
]

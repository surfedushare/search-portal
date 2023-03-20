from django.urls import path

from search import views


app_name = 'search'
public_api_patterns = [
    path(r'search/research-products', views.ResearchProductSearchAPIView.as_view(), name="research-product"),
    path(r'search/learning-materials', views.LearningMaterialSearchAPIView.as_view(), name="research-product"),
]
urlpatterns = public_api_patterns

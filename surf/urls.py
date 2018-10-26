"""surf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from rest_framework import routers

from surf.apps.materials.views import (
    MaterialSearchAPIView,
    KeywordsAPIView,
    MaterialAPIView,
    CollectionViewSet
)

from surf.apps.filters.views import (
    FilterCategoryViewSet,
    FilterViewSet
)

admin.site.site_header = 'Surf'
admin.site.site_title = 'Surf'
admin.site.index_title = 'Surf'

default_router = routers.DefaultRouter()

default_router.register(r'filter-categories', FilterCategoryViewSet)
default_router.register(r'filters', FilterViewSet)
default_router.register(r'collections', CollectionViewSet)

apipatterns = [
    url(r'^keywords/', KeywordsAPIView.as_view()),
    url(r'^materials/search/', MaterialSearchAPIView.as_view()),
    url(r'^materials/', MaterialAPIView.as_view()),
] + default_router.urls

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    path('admin/', admin.site.urls),
    url(r'^api/(?P<version>(v1))/', include(apipatterns)),
]

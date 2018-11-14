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
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static

from surf.routers import CustomRouter

from surf.apps.materials.views import (
    MaterialSearchAPIView,
    KeywordsAPIView,
    MaterialAPIView,
    CollectionViewSet,
    ApplaudMaterialViewSet
)

from surf.apps.filters.views import (
    FilterCategoryViewSet,
    FilterViewSet
)

from surf.apps.users.views import (
    auth_begin_handler,
    auth_complete_handler,
    login_handler
)

from surf.apps.communities.views import CommunityViewSet

admin.site.site_header = 'Surf'
admin.site.site_title = 'Surf'
admin.site.index_title = 'Surf'

router = CustomRouter()
router.register(r'filter-categories', FilterCategoryViewSet)
router.register(r'filters', FilterViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'applaud-materials', ApplaudMaterialViewSet)
router.register(r'communities', CommunityViewSet)

apipatterns = [
    url(r'^login/', login_handler),
    url(r'^keywords/', KeywordsAPIView.as_view()),
    url(r'^materials/search/', MaterialSearchAPIView.as_view()),
    url(r'^materials/', MaterialAPIView.as_view()),
] + router.urls

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    path('admin/', admin.site.urls),
    url(r'^api/(?P<version>(v1))/', include(apipatterns)),

    url(r'^login/surfconext/', auth_begin_handler),
    url(r'^complete/surfconext/', auth_complete_handler),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

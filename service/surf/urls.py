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
from django.conf.urls import url, include
from django.urls import path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from surf.routers import CustomRouter
from surf.apps.materials.views import (
    portal_single_page_application,
    MaterialSearchAPIView,
    KeywordsAPIView,
    MaterialAPIView,
    MaterialRatingAPIView,
    MaterialApplaudAPIView,
    CollectionViewSet,
    CollectionMaterialPromotionAPIView,
)
from surf.apps.filters.views import (
    FilterCategoryViewSet,
    FilterViewSet,
    MpttFilterItems
)
from surf.apps.users.views import (
    UserDetailsAPIView,
    ObtainTokenAPIView
)
from surf.apps.core.views import health_check
from surf.apps.communities.views import CommunityViewSet
from surf.apps.themes.views import ThemeViewSet
from surf.apps.stats.views import StatsView
from surf.apps.locale.views import get_localisation_strings

admin.site.site_header = 'Surf'
admin.site.site_title = 'Surf'
admin.site.index_title = 'Surf'

router = CustomRouter()
router.register(r'filter-categories', FilterCategoryViewSet, basename='MpttFilterItem')
router.register(r'filters', FilterViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'communities', CommunityViewSet)
router.register(r'themes', ThemeViewSet)
router.register(r'stats', StatsView, base_name="stats")

apipatterns = [
    url(r'^users/me/', UserDetailsAPIView.as_view()),
    url(r'^users/obtain-token/', ObtainTokenAPIView.as_view()),
    url(r'^keywords/', KeywordsAPIView.as_view()),
    url(r'^rate_material/', MaterialRatingAPIView.as_view()),
    url(r'^applaud_material/', MaterialApplaudAPIView.as_view()),
    url(r'^materials/search/', MaterialSearchAPIView.as_view()),
    url(r'^materials/(?P<external_id>.+)/', MaterialAPIView.as_view()),
    url(r'^materials/', MaterialAPIView.as_view()),
    url(r'^localehtml/', MaterialAPIView.as_view()),
    url(r'^filteritems/', MpttFilterItems.as_view()),
    url(r'^collections/(?P<collection_id>.+)/promote_material/(?P<external_id>.+)/',
        CollectionMaterialPromotionAPIView.as_view()),
] + router.urls

urlpatterns = [
    url(r'^health/?$', health_check, name="health-check"),
    url('', include('social_django.urls', namespace='social')),
    url(r'^logout/?$', auth_views.LogoutView.as_view(success_url_allowed_hosts=settings.ALLOWED_REDIRECT_HOSTS)),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/(?P<version>(v1))/', include(apipatterns)),
    url(r'^locales/(?P<locale>en|nl)/?$', get_localisation_strings),
    url(r'^$', portal_single_page_application, name="portal-spa"),
    url(r'^.*/$', portal_single_page_application),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # ignored in production

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

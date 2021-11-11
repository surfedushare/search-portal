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
import os

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.conf.urls import url, include
from django.urls import path
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from surf.sitemap import MainSitemap, MaterialsSitemap
from surf.routers import CustomRouter
from surf.apps.materials.views import (
    portal_material,
    portal_single_page_application,
    MaterialSearchAPIView,
    MaterialSetAPIView,
    KeywordsAPIView,
    SimilarityAPIView,
    AuthorSuggestionsAPIView,
    MaterialAPIView,
    MaterialRatingAPIView,
    MaterialApplaudAPIView,
    CollectionViewSet,
    CollectionMaterialPromotionAPIView,
)
from surf.apps.filters.views import FilterCategoryView
from surf.apps.users.views import (
    DeleteAccountAPIView,
    UserDetailsAPIView,
    ObtainTokenAPIView
)
from surf.apps.core.views import health_check, robots_txt
from surf.apps.communities.views import CommunityViewSet
from surf.apps.themes.views import ThemeViewSet
from surf.apps.stats.views import StatsViewSet, StatsView
from surf.apps.locale.views import get_localisation_strings
from surf.apps.feedback.views import FeedbackAPIView


admin.site.site_header = 'Surf'
admin.site.site_title = 'Surf'
admin.site.index_title = 'Surf'


public_api_patterns = [
    url(r'^search/filter-categories/', FilterCategoryView.as_view()),
    url(r'^search/autocomplete/', KeywordsAPIView.as_view()),
    url(r'^search/', MaterialSearchAPIView.as_view()),
    url(r'^documents/stats', StatsView.as_view()),
    url(r'^suggestions/similarity/', SimilarityAPIView.as_view()),
    url(r'^suggestions/author/', AuthorSuggestionsAPIView.as_view()),
]
schema_view = get_schema_view(
    title="Search API",
    description="An API that allows search through Elastic Search. Instead of writing Elastic queries "
                "search can be done simply by passing a few parameters to the endpoints.",
    patterns=public_api_patterns,
    url="/api/v1/"
)
swagger_view = TemplateView.as_view(
    template_name='swagger/swagger-ui.html',
    extra_context={'schema_url': 'openapi-schema'}
)


router = CustomRouter()
router.register(r'collections', CollectionViewSet)
router.register(r'communities', CommunityViewSet)
router.register(r'themes', ThemeViewSet)
router.register(r'stats', StatsViewSet, basename="stats")


apipatterns = public_api_patterns + router.urls + [
    path('openapi', schema_view, name='openapi-schema'),
    path('docs/', swagger_view, name='docs'),
    url(r'^users/me/', UserDetailsAPIView.as_view()),
    url(r'^users/delete-account/', DeleteAccountAPIView.as_view()),
    url(r'^users/obtain-token/', ObtainTokenAPIView.as_view()),
    url(r'^rate_material/', MaterialRatingAPIView.as_view()),
    url(r'^applaud_material/', MaterialApplaudAPIView.as_view()),
    url(r'^materials/set/', MaterialSetAPIView.as_view()),
    url(r'^materials/search/', MaterialSearchAPIView.as_view()),
    url(r'^filter-categories/', FilterCategoryView.as_view()),
    url(r'^keywords/', KeywordsAPIView.as_view()),
    url(r'^materials/(?P<external_id>.+)/', MaterialAPIView.as_view()),
    url(r'^materials/', MaterialAPIView.as_view()),
    url(r'^collections/(?P<collection_id>.+)/promote_material/(?P<external_id>.+)/',
        CollectionMaterialPromotionAPIView.as_view()),
    url(r'^feedback/', FeedbackAPIView.as_view())
]

sitemaps = {
    "main": MainSitemap,
    "materials": MaterialsSitemap
}

urlpatterns = [
    # System
    url(r'^health/?$', health_check, name="health-check"),

    # Authentication
    # Catching frontend login endpoints before social auth handles "login" prefix
    url(r'^login/(permissions|success)/?', portal_single_page_application),
    url('', include('social_django.urls', namespace='social')),
    url(r'^logout/?$', auth_views.LogoutView.as_view(success_url_allowed_hosts=settings.ALLOWED_REDIRECT_HOSTS)),

    # Admin interface
    url(r'^admin/', admin.site.urls),

    # API and other data
    url(r'^api/v1/', include(apipatterns)),
    url(r'^locales/(?P<locale>en|nl)/?$', get_localisation_strings),

    # For crawlers
    path('sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps}, name="sitemap-index"),
    path('sitemap-<section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps},
         name="django.contrib.sitemaps.views.sitemap"),
    path('robots.txt', robots_txt)
]

if settings.PROJECT == "edusources":
    # Translated frontend patterns
    urlpatterns += i18n_patterns(
        url(_(r'^materialen/zoeken/?'), portal_single_page_application, name="portal-search"),
        url(_(r'^materialen/(?P<external_id>.+)/'), portal_material),
        url(r'^$', portal_single_page_application, name="portal-spa"),
        url(r'^.*/$', portal_single_page_application),
        prefix_default_language=False
    )
else:
    urlpatterns += [
        url(r'^$', health_check),
    ]


if settings.MODE == 'localhost':
    # These patterns are ignored in production, but are needed for localhost media and some static files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static("/images/", document_root=os.path.join(settings.PORTAL_BASE_DIR, "images"))

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


handler404 = 'surf.apps.materials.views.portal_page_not_found'

"""harvester URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from core import views as core_views
from core.urls import public_api_patterns as core_public


api_description = """
An API that allows downloading all data from a dataset as well as extending data with custom values.

To authenticate with the API you either need to login to the admin (useful to use this interactive documentation).
Or you have to send an Authorization header with a value of "Token <your-api-token>" (recommended).
"""
schema_view = get_schema_view(
    title="Harvester API",
    description=api_description,
    patterns=core_public,
    url="/api/v1/"
)
swagger_view = TemplateView.as_view(
    template_name='swagger/swagger-ui.html',
    extra_context={'schema_url': 'v1:openapi-schema'}
)


api_urlpatterns = [
    path('openapi/', schema_view, name='openapi-schema'),
    path('docs/', swagger_view, name='docs'),
    path('', include('core.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include((api_urlpatterns, "v1",))),
    path('', core_views.health_check, name="health-check")
]


# We provide *insecure* access to harvester content when dealing with local storage (aka localhost development)
if not settings.IS_AWS:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

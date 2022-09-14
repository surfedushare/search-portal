from django.conf import settings
from django.apps import apps
from django.shortcuts import render, Http404
from django.views.decorators.gzip import gzip_page
from rest_framework.renderers import JSONRenderer

from surf.apps.locale.models import Locale
from surf.apps.filters.serializers import MpttFilterItemSerializer
from surf.apps.materials.views.search import _get_material_by_external_id


filters_app = apps.get_app_config("filters")


@gzip_page
def portal_material(request, *args, **kwargs):
    material = _get_material_by_external_id(request, kwargs["external_id"])
    if not material:
        raise Http404(f"Material not found: {kwargs['external_id']}")
    return render(request, "portal/index.html", {
        'meta_title': f"{material[0]['title']} | Edusources",
        'meta_description': material[0]["description"],
        'matomo_id': settings.MATOMO_ID
    })


@gzip_page
def portal_single_page_application(request, *args):
    site_description_translation = Locale.objects.filter(asset="meta-site-description").last()
    site_description = getattr(site_description_translation, request.LANGUAGE_CODE, "Edusources")
    filter_category_tree = filters_app.metadata.tree
    filter_categories = MpttFilterItemSerializer(
        filter_category_tree,
        many=True
    )
    return render(request, "portal/index.html", {
        'meta_title': "Edusources",
        'meta_description': site_description,
        'matomo_id': settings.MATOMO_ID,
        'filter_categories_json': JSONRenderer().render(filter_categories.data).decode("utf-8")
    })


@gzip_page
def portal_page_not_found(request, exception, template_name=None):
    site_description_translation = Locale.objects.filter(asset="meta-site-description").last()
    site_description = getattr(site_description_translation, request.LANGUAGE_CODE, "Edusources")
    return render(
        request,
        "portal/index.html",
        context={
            'meta_title': "Edusources",
            'meta_description': site_description,
            'matomo_id': settings.MATOMO_ID
        },
        status=404
    )

from django.apps import apps
from django.shortcuts import render, HttpResponse
from django.views.decorators.gzip import gzip_page
from rest_framework.exceptions import ValidationError

from surf.vendor.search.api import SearchApiClient
from surf.apps.materials.serializers import SearchSerializer


filters_app = apps.get_app_config("filters")


@gzip_page
def widget_iframe_content(request):
    serializer = SearchSerializer(data=request.GET)
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError as exc:
        return HttpResponse(exc, status=400)
    data = serializer.validated_data
    data["drilldown_names"] = filters_app.metadata.get_filter_field_names()
    client = SearchApiClient()
    res = client.search(**data)
    records = res["records"]
    return render(request, "widget/index.html", {
        "records": records
    })

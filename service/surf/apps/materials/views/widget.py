import json
from dateutil.parser import parse as date_parser

from django.apps import apps
from django.shortcuts import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.gzip import gzip_page
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework.exceptions import ValidationError

from surf.vendor.search.api import SearchApiClient
from surf.apps.materials.serializers import SearchSerializer
from surf.apps.materials.utils import add_extra_parameters_to_materials


filters_app = apps.get_app_config("filters")


@xframe_options_exempt
@gzip_page
def widget_iframe_content(request):
    # Validates incoming data
    data = request.GET.dict()
    data["search_text"] = data["search_text"] if data["search_text"] != '""' else ""
    if "filters" in data:
        data["filters"] = json.loads(data["filters"])
    serializer = SearchSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError as exc:
        return HttpResponse(exc, status=400)
    data = serializer.validated_data
    # Transforms incoming data for search request
    data["filters"] = [
        {"external_id": external_id, "items": items}
        for external_id, items in data["filters"].items()
    ]
    data["drilldown_names"] = filters_app.metadata.get_filter_field_names()
    client = SearchApiClient()
    res = client.search(**data)
    records = res["records"]
    for record in records:
        if not record["published_at"]:
            continue
        record["published_at"] = date_parser(record["published_at"])
    records = add_extra_parameters_to_materials(filters_app.metadata, records)
    return TemplateResponse(
        request=request,
        template="widget/index.html",
        context={
            "records": records,
            "record_count": res["recordcount"],
            "technical_type_translations": {
                technical_type: translations[request.LANGUAGE_CODE]
                for technical_type, translations in filters_app.metadata.translations["technical_type"].items()
            },
        }
    )

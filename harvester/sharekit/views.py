import json
from sentry_sdk import capture_message

from django.conf import settings
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from datagrowth.configuration import create_config

from harvester.utils.extraction import prepare_seed
from core.logging import HarvestLogger
from core.models import DatasetVersion
from sharekit.extraction import SharekitMetadataExtraction, create_objective


@csrf_exempt
def edit_document_webhook(request, channel, secret):
    # Webhook validation
    if str(secret) != settings.HARVESTER_WEBHOOK_SECRET:
        return HttpResponse(status=403, reason="Webhook not allowed in this environment")
    if request.META["HTTP_X_FORWARDED_FOR"] not in ["20.56.15.206", "20.56.8.62"]:
        capture_message(
            f"edit_document_webhook called from invalid IP: {request.META['HTTP_X_FORWARDED_FOR']}",
            level="warning"
        )
        return HttpResponse(status=403, reason="Webhook not allowed from source")
    try:
        data = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        return HttpResponse(status=400, reason="Invalid JSON")
    if isinstance(data["attributes"], list):
        data["attributes"] = {}
    # Processing of incoming data
    extract_config = create_config("extract_processor", {
        "objective": create_objective(root="$", include_is_restricted=False)
    })
    prc = SharekitMetadataExtraction(config=extract_config)
    seed = next(prc.extract("application/json", data))
    seed["is_restricted"] = channel == "edusourcesprivate"
    prepare_seed(seed)
    # Commit changes to the database
    dataset_version = DatasetVersion.objects.get_current_version()
    collection = dataset_version.collection_set.filter(name=channel).last()
    collection.update([seed], "external_id")
    # Finish webhook request
    logger = HarvestLogger(dataset_version.dataset.name, "edit_document_webhook", {})
    logger.report_material(seed["external_id"], title=seed["title"], url=seed["url"])
    return HttpResponse("ok")

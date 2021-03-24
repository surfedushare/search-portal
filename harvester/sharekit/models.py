import json
from urlobject import URLObject

from django.conf import settings

from core.models import HarvestHttpResource


class SharekitMetadataHarvest(HarvestHttpResource):

    URI_TEMPLATE = "https://api.surfsharekit.nl/api/jsonapi/channel/v1/{}/repoItems?filter[modified][GE]={}"
    PARAMETERS = {
        "page[size]": 50
    }

    def auth_headers(self):
        return {
            "Authorization": f"Bearer {settings.SHAREKIT_API_KEY}"
        }

    def next_parameters(self):
        content_type, data = self.content
        next_link = data["links"].get("next", None)
        if not next_link:
            return {}
        next_url = URLObject(next_link)
        return {
            "page[number]": next_url.query_dict["page[number]"]
        }

    @property
    def content(self):
        if self.success:
            content_type = self.head.get("content-type", "unknown/unknown").split(';')[0]
            if content_type == "application/vnd.api+json":
                return content_type, json.loads(self.body)
            else:
                return content_type, None
        return None, None

    class Meta:
        verbose_name = "Sharekit metadata harvest"
        verbose_name_plural = "Sharekit metadata harvest"

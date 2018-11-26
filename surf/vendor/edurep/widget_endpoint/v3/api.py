import requests

_DEFAULT_API_ENDPOINT = "https://proxy.edurep.nl/v3/search"

_BASE_QUERY = "edurep"


class WidgetEndpointApiClient:

    def __init__(self, api_endpoint=_DEFAULT_API_ENDPOINT):
        self.api_endpoint = api_endpoint

    def drilldowns(self, drilldown_names, query=None):
        if query:
            query = '{} AND ("{}")'.format(_BASE_QUERY, query)
        else:
            query = _BASE_QUERY

        url = "{}?mode=json&query={}&maximumRecords=0&x-term-drilldown={}".format(
            self.api_endpoint,
            query,
            ",".join(drilldown_names))

        response = requests.get(url)

        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()

        try:
            return response.json()["search"]["drilldowns"]
        except KeyError:
            return dict()

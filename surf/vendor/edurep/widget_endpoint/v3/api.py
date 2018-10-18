import requests

_API_ENDPOINT = "https://proxy.edurep.nl/v3/search"

_BASE_QUERY = "edurep"


class WidgetEndpointApiClient:

    def drilldowns(self, drilldown_names, query=None):
        if not query:
            query = _BASE_QUERY
        else:
            query = '{} AND ("{}")'.format(_BASE_QUERY, query)

        url = "{}?mode=json&query={}&maximumRecords=0&x-term-drilldown={}".format(
            _API_ENDPOINT,
            query,
            ",".join(drilldown_names))
        response = requests.get(url)
        try:
            return response.json()["search"]["drilldowns"]
        except KeyError:
            return dict()

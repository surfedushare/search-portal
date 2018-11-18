import requests

_API_ENDPOINT = "https://proxy.edurep.nl/v3/search"

_BASE_QUERY = "edurep"


class WidgetEndpointApiClient:

    def drilldowns(self, drilldown_names, query=None):
        if query:
            query = '{} AND ("{}")'.format(_BASE_QUERY, query)
        else:
            query = _BASE_QUERY

        url = "{}?mode=json&query={}&maximumRecords=0&x-term-drilldown={}".format(
            _API_ENDPOINT,
            query,
            ",".join(drilldown_names))

        response = requests.get(url)

        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()

        try:
            return response.json()["search"]["drilldowns"]
        except KeyError:
            return dict()

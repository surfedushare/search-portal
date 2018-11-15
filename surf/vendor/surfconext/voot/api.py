import requests

_DEFAULT_API_ENDPOINT = "https://voot.surfconext.nl"


class VootApiClient:

    def __init__(self, api_endpoint):
        if api_endpoint:
            self.api_endpoint = api_endpoint
        else:
            self.api_endpoint = _DEFAULT_API_ENDPOINT

    def get_groups(self, access_token):
        headers = {
            "Authorization": "bearer {}".format(access_token)
        }

        url = "{}/me/groups/".format(self.api_endpoint)
        response = requests.get(url, headers=headers)

        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()

        return response.json()

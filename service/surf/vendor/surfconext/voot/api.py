"""
This module provides integration with VOOT API (SURFconext).
"""

import requests

_DEFAULT_API_ENDPOINT = "https://voot.surfconext.nl"


class VootApiClient:
    """
    Class provides integration with VOOT API
    """

    def __init__(self, api_endpoint):
        if api_endpoint:
            self.api_endpoint = api_endpoint
        else:
            self.api_endpoint = _DEFAULT_API_ENDPOINT

    def get_groups(self, access_token):
        """
        Returns SURFconext groups by user access token
        :param access_token: user access token
        """
        headers = {
            "Authorization": "bearer {}".format(access_token)
        }

        url = "{}/me/groups/".format(self.api_endpoint)
        response = requests.get(url, headers=headers)

        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()

        return response.json()

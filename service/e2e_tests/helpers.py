import os
import json
from unittest.mock import patch, MagicMock
from time import sleep

from django.conf import settings

from surf.apps.users.models import SessionToken


filter_categories_file_path = os.path.join(
    settings.BASE_DIR, "apps", "filters", "fixtures", "metadata-tree.json"
)
with open(filter_categories_file_path) as filter_categories_file:
    METADATA_TREE = json.load(filter_categories_file)


def get_metadata_tree_mock(*args, **kwargs):
    mock = MagicMock()
    mock.json = MagicMock(return_value=METADATA_TREE)
    mock.status_code = 200
    return mock


# Fake a logged in user by setting surf_token in the local storage
def login(self, user):
    token, created = SessionToken.objects.get_or_create(user=user)
    with patch("surf.apps.filters.metadata.requests.get", new=get_metadata_tree_mock):
        self.selenium.get(self.live_server_url)
        sleep(10)
    self.selenium.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", "surf_token", token.key)


def replace_content(element, text):
    element.click()
    element.clear()
    element.send_keys(text)

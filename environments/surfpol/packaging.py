import os
import json
import logging


logger = logging.getLogger(__file__)


def get_package_info():
    info_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "info.json")
    if not os.path.exists(info_file_path):
        logger.warning("Can't find info.json in environment directory. Perhaps 'invoke prepare-builds' will help?")
        return {"versions": {}}
    with open(info_file_path) as info_file:
        info = json.load(info_file)
    return info

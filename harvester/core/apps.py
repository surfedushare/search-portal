from django.apps import AppConfig
from django.conf import settings

from datagrowth.configuration import register_defaults


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):

        register_defaults("global", {
            "purge_after": {"days": 30}
        })
        register_defaults("micro_service", {
            "connections": {
                "analyzer": {
                    "protocol": "http",
                    "host": "localhost:9090" if settings.IS_AWS or settings.CONTEXT == "host" else "analyzer:9090",
                    "path": "/analyze"
                }
            }
        })

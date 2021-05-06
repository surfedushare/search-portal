from django.apps import AppConfig

from datagrowth.configuration import register_defaults


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        register_defaults("global", {
            "purge_after": {"days": 30}
        })

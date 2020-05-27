from django.core.management.commands import runserver


class Command(runserver.Command):
    default_port = "8888"

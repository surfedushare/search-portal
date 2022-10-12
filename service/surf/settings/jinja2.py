from datetime import datetime

from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation
from django.utils.formats import date_format

from jinja2 import Environment


def environment(**options):
    options["extensions"] += ["jinja2.ext.i18n"]
    env = Environment(**options)
    env.install_gettext_translations(translation)
    env.globals.update({
        'static': static,
        'url': reverse,
        'datetime': datetime,
        'date_format': date_format
    })
    return env

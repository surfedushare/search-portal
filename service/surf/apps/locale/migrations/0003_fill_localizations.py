# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


LOCALIZATIONS_EN = {}

LOCALIZATIONS_NL = {}


def fill_localizations(apps, schema_editor):
    Locale = apps.get_model('locale', 'Locale')

    localizations = dict()
    for k, v in LOCALIZATIONS_EN.items():
        localizations.setdefault(k, {})["en"] = v

    for k, v in LOCALIZATIONS_NL.items():
        localizations.setdefault(k, {})["nl"] = v

    for k, v in localizations.items():
        Locale.objects.create(asset=k, en=v.get("en", ""), nl=v.get("nl", ""))


class Migration(migrations.Migration):

    dependencies = [
        ('locale', '0002_auto_20190329_1026'),
    ]

    operations = [
        migrations.RunPython(fill_localizations,
                             migrations.RunPython.noop),
    ]

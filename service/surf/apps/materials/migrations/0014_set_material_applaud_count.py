# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_applaud_count(apps, schema_editor):
    ApplaudMaterial = apps.get_model('materials', 'ApplaudMaterial')
    ApplaudMaterial.objects.update(applaud_count=1)


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0013_auto_20190214_1026'),
    ]

    operations = [
        migrations.RunPython(update_applaud_count,
                             migrations.RunPython.noop),
    ]

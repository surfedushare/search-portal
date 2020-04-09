# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_applaud_count(apps, schema_editor):
    Material = apps.get_model('materials', 'Material')

    for m in Material.objects.all():
        m.applaud_count = m.applauds.count() if m.applauds else 0
        m.save()


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0011_material_applaud_count'),
    ]

    operations = [
        migrations.RunPython(update_applaud_count,
                             migrations.RunPython.noop),
    ]

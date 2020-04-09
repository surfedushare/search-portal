# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_surf_teams(apps, schema_editor):
    SurfTeam = apps.get_model('communities', 'SurfTeam')
    Community = apps.get_model('communities', 'Community')

    for c in Community.objects.all():
        t = SurfTeam.objects.create(external_id=c.external_id,
                                    name=c.name,
                                    description=c.description)

        if c.admins:
            t.admins.set(c.admins.all())

        if c.members:
            t.members.set(c.members.all())

        c.surf_team = t
        c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0003_auto_20181210_1031'),
    ]

    operations = [
        migrations.RunPython(create_surf_teams,
                             migrations.RunPython.noop),
    ]

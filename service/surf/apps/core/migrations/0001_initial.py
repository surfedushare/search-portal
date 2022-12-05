from django.conf import settings
from django.db import migrations
from django.contrib.sites.models import Site


def rename_site(apps, schema_editor):
    if settings.PROJECT == "nppo":
        main_name = "Publinova"
        main_domain = "search.publinova.nl"
    else:
        main_name = "Edusources"
        main_domain = "edusources.nl"
    if not Site.objects.all().exists():
        Site.objects.create(domain=main_domain, name=main_name)
    else:
        Site.objects.filter(id=1).update(domain=main_domain, name=main_name)
    mbo_site = Site.objects.filter(id=2).last()
    if mbo_site is None and settings.PROJECT == "edusources":
        Site.objects.create(domain="harvester.mbo.prod.surfedushare.nl", name="MBO Edusources")


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(rename_site)
    ]
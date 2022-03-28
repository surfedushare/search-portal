from django.db import migrations


def migrate_is_current_flag(apps, schema_editor):
   DatasetVersion = apps.get_model("core.DatasetVersion")
   latest_version = DatasetVersion.objects.filter(is_current=True).last()
   if not latest_version:
       return
   DatasetVersion.objects.filter(is_current=True).exclude(id=latest_version.id).update(is_current=False)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_dataset_version_order'),
    ]

    operations = [
        migrations.RunPython(
            migrate_is_current_flag,
            migrations.RunPython.noop
        )
    ]

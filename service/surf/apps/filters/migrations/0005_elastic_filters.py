from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filters', '0004_allow_identical_external_ids'),
    ]

    operations = [
        migrations.RunPython(
            migrations.RunPython.noop,
            migrations.RunPython.noop
        )
    ]

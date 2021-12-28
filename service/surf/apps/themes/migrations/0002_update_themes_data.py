from django.db import migrations


def update_theme_data(apps, schema_editor):
    Theme = apps.get_model("themes.Theme")
    for theme in Theme.objects.select_related("filter_category_item").all():
        theme.delete()
        theme.id = theme.filter_category_item.id
        theme.external_id = theme.filter_category_item.external_id
        theme.save()


class Migration(migrations.Migration):

    dependencies = [
        ('themes', '0001_squashed_0007_predictable_theme_ordering'),
    ]

    operations = [
        migrations.RunPython(
            update_theme_data,
            migrations.RunPython.noop
        )
    ]

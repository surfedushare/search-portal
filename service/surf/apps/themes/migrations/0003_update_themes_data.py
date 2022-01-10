from django.db import migrations
from django.utils.text import slugify


def update_theme_data(apps, schema_editor):
    Theme = apps.get_model("themes.Theme")
    for theme in Theme.objects.select_related("filter_category_item").all():
        theme.delete()
        theme.id = theme.filter_category_item.id
        theme.external_id = theme.filter_category_item.external_id
        theme.nl_slug = slugify(theme.filter_category_item.title_translations.nl)
        theme.en_slug = slugify(theme.filter_category_item.title_translations.en)
        theme.save()


class Migration(migrations.Migration):

    dependencies = [
        ('themes', '0002_theme_slugs'),
    ]

    operations = [
        migrations.RunPython(
            update_theme_data,
            migrations.RunPython.noop
        )
    ]

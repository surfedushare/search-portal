# Generated by Django 2.2.13 on 2020-11-05 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0027_predictable_theme_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionmaterial',
            name='position',
            field=models.IntegerField(default=0),
        ),
    ]

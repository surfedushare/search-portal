# Generated by Django 2.2.13 on 2021-03-10 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filters', '0001_squashed_0016_filters_external_id_unique'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mpttfilteritem',
            name='enabled_by_default',
        ),
        migrations.AddField(
            model_name='mpttfilteritem',
            name='is_manual',
            field=models.BooleanField(default=False),
        ),
    ]
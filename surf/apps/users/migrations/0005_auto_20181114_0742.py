# Generated by Django 2.0.6 on 2018-11-14 07:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20181113_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surfconextauth',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='surfconext_auth', to=settings.AUTH_USER_MODEL),
        ),
    ]

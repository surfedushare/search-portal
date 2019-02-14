# Generated by Django 2.0.10 on 2019-02-14 10:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0012_set_material_applaud_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='applaud_count',
        ),
        migrations.AddField(
            model_name='applaudmaterial',
            name='applaud_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='applaudmaterial',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applauds', to=settings.AUTH_USER_MODEL),
        ),
    ]

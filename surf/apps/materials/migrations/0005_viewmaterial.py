# Generated by Django 2.0.6 on 2018-11-08 20:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('materials', '0004_applaudmaterial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewMaterial',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='material_views', to='materials.Material')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='material_views', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# Generated by Django 2.1.2 on 2018-10-15 10:33

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FilterCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('edurep_field_id', models.CharField(max_length=255, verbose_name='Field id in EduRep')),
                ('max_item_count', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FilterCategoryItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('external_id', models.CharField(max_length=255, verbose_name='Filter item id in EduRep')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='filters.FilterCategory', verbose_name='Filter category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FilterItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('category_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filter_items', to='filters.FilterCategoryItem')),
                ('filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='filters.Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

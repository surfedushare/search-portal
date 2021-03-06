# Generated by Django 2.2.13 on 2020-12-14 12:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# surf.apps.themes.migrations.0005_auto_20190830_0813

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('filters', '0001_squashed_0016_filters_external_id_unique'),
        ('locale', '0004_improved_translations'),
    ]

    operations = [
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('external_id', models.CharField(max_length=255)),
                ('description_translations', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='locale.LocaleHTML')),
                ('title_translations', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='locale.Locale')),
                ('mptt_disciplines', models.ManyToManyField(blank=True, related_name='parent_themes', to='filters.MpttFilterItem')),
                ('mptt_filter_category_item', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='theme', to='filters.MpttFilterItem')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='theme',
            old_name='mptt_disciplines',
            new_name='disciplines',
        ),
        migrations.RenameField(
            model_name='theme',
            old_name='mptt_filter_category_item',
            new_name='filter_category_item',
        ),
        migrations.AlterModelOptions(
            name='theme',
            options={'ordering': ('created_at',)},
        ),
        migrations.AddField(
            model_name='theme',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

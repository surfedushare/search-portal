# Generated by Django 2.0.13 on 2019-11-04 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0019_auto_20191104_1226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='materials',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='owner',
        ),
        migrations.RenameField(
            model_name='collection',
            old_name='new_materials',
            new_name='materials',
        ),
        migrations.AlterField(
            model_name='collection',
            name='materials',
            field=models.ManyToManyField(blank=True, related_name='collections', through='materials.CollectionMaterial', to='materials.Material'),
        ),
    ]

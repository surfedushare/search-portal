# Generated by Django 2.0.13 on 2019-11-04 10:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_enumfield.db.fields
import surf.statusenums


def copy_materials_to_new_collections(apps, schema_editor):
    Collection = apps.get_model('materials', 'Collection')
    CollectionMaterial = apps.get_model('materials', 'CollectionMaterial')

    for collection in Collection.objects.all():
        for material in collection.materials.all():
            CollectionMaterial.objects.create(collection=collection, material=material)

        collection.save()


def remove_new_materials(apps, schema_editor):
    Collection = apps.get_model('materials', 'Collection')

    for collection in Collection.objects.all():
        collection.new_materials.clear()
        collection.save()


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0018_auto_20190830_0934'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('featured', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Material',
            },
        ),
        migrations.AddField(
            model_name='collection',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='publish_status',
            field=django_enumfield.db.fields.EnumField(default=0, enum=surf.statusenums.PublishStatus),
        ),
        migrations.AddField(
            model_name='material',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='materials',
            field=models.ManyToManyField(blank=True, related_name='new_collections', through='materials.CollectionMaterial', to='materials.Material'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='collections', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='collectionmaterial',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='materials.Collection'),
        ),
        migrations.AddField(
            model_name='collectionmaterial',
            name='material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='materials.Material'),
        ),
        migrations.RunPython(copy_materials_to_new_collections, remove_new_materials)
    ]

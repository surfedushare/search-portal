# Generated by Django 2.2.20 on 2021-04-30 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_harvest_refactor_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elasticindex',
            name='dataset_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='indices', to='core.DatasetVersion'),
        ),
    ]

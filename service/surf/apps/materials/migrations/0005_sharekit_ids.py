from collections import defaultdict

from django.db import migrations


def migrate_sharekit_identifiers_2(apps, schema_editor):
    # Group all materials by their normalized id
    Material = apps.get_model("materials.Material")
    materials_by_id = defaultdict(list)
    for material in Material.objects.filter(external_id__startswith="surf"):
        external_id_parts = material.external_id.split(":")
        external_id = external_id_parts[-1]
        materials_by_id[external_id].append(material)
    # Adjust all materials based on how many copies exist
    for external_id, materials in materials_by_id.items():
        # First we'll set the external_id
        material = materials[0]
        material.external_id = external_id
        # And we stop if we don't need to merge
        if len(materials) == 1:
            material.save()
            continue
        # Or we merge all extra materials and delete the extra ones
        for extra_material in materials[1:]:
            material.star_1 += extra_material.star_1
            material.star_2 += extra_material.star_2
            material.star_3 += extra_material.star_3
            material.star_4 += extra_material.star_4
            material.star_5 += extra_material.star_5
            material.view_count += extra_material.view_count
            material.applaud_count += extra_material.applaud_count
            for extra_collection in extra_material.collections.all():
                if extra_collection not in material.collections.all():
                    material.collections.add(extra_collection)
            extra_material.delete()
        material.save()


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0004_strip_materials'),
    ]

    operations = [
        migrations.RunPython(
            migrate_sharekit_identifiers_2,
            migrations.RunPython.noop
        ),
    ]

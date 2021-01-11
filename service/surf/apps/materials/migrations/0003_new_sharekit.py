from django.db import migrations


LEGACY_SHAREKIT_PREFIXES = [
    "fontys",
    "inholland",
    "oer_che",
    "oer_han",
    "oer_hr",
    "oer_hsleiden",
    "oer_hu",
    "oer_hva",
    "oer_nhlstenden",
    "oer_rug",
    "oer_um",
    "oer_uvt",
    "oer_vu",
    "oer_wur",
    "oer_zuyd",
    "pubaflsinholland",
    "surf",
    "tu_ethics",
    "tu_urbanresilience",
]


def migrate_sharekit_identifiers(apps, schema_editor):
    Material = apps.get_model("materials.Material")
    for prefix in LEGACY_SHAREKIT_PREFIXES:
        materials = []
        for material in Material.objects.filter(external_id__startswith=prefix + ":"):
            material.external_id = material.external_id.replace(prefix, "surfsharekit", 1)
            materials.append(material)
        Material.objects.bulk_update(materials, fields=["external_id"])


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0002_collection_position'),
    ]

    operations = [
        migrations.RunPython(
            migrate_sharekit_identifiers,
            migrations.RunPython.noop
        ),
    ]

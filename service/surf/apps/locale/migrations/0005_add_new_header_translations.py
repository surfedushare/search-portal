from django.db import migrations

def add_asset_data(apps, schema_editor):
    Asset = apps.get_model('locale', 'Locale')
    Asset.objects.create(asset='navigation.find-material', en='Find learning material', nl='Vind leermateriaal')
    Asset.objects.create(asset='navigation.communities', en='Communities', nl='Community\'s')
    Asset.objects.create(asset='navigation.services', en='Services', nl='Services')
    Asset.objects.create(asset='navigation.upload', en='Upload', nl='Upload')
    Asset.objects.create(asset='navigation.signin', en='Sign in', nl='Inloggen')
    Asset.objects.create(asset='navigation.signout', en='Sign out', nl='Uitloggen')
    Asset.objects.create(asset='navigation.my-institution', en='My institution', nl='Mijn instelling')

class Migration(migrations.Migration):

    dependencies = [
        ('locale', '0004_improved_translations'),
    ]

    operations = [
        migrations.RunPython(add_asset_data),
    ]

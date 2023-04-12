from django.db import migrations

def add_asset_data(apps, schema_editor):
    Asset = apps.get_model('locale', 'Locale')
    Asset.objects.create(asset='navigation.find-material', en='Search learning material', nl='Zoek leermateriaal')
    Asset.objects.create(asset='navigation.communities', en='Communities', nl='Community\'s')
    Asset.objects.create(asset='navigation.services', en='Knowledge and expertise', nl='Kennis en expertise')
    Asset.objects.create(asset='navigation.upload', en='Upload', nl='Upload')
    Asset.objects.create(asset='navigation.signin', en='Sign in', nl='Inloggen')
    Asset.objects.create(asset='navigation.signout', en='Sign out', nl='Uitloggen')
    Asset.objects.create(asset='navigation.my-institution', en='My institution', nl='Mijn instelling')
    Asset.objects.create(asset='footer.about', en='About edusources', nl='Over edusources')
    Asset.objects.create(asset='footer.institutions', en='Participating institutions', nl='Deelnemende instellingen')
    Asset.objects.create(asset='footer.privacy', en='Privacy', nl='Privacy')

class Migration(migrations.Migration):

    dependencies = [
        ('locale', '0004_improved_translations'),
    ]

    operations = [
        migrations.RunPython(add_asset_data),
    ]

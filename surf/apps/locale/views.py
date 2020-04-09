from itertools import chain

from rest_framework.decorators import api_view
from rest_framework.response import Response

from surf.vendor.surfconext.models import PrivacyStatement
from surf.apps.locale.models import Locale, LocaleHTML


@api_view()
def get_localisation_strings(request, locale):
    translations = chain(Locale.objects.iterator(), LocaleHTML.objects.iterator())
    data = {
        translation.translation_key: getattr(translation, locale, None)
        for translation in translations
    }
    # Most translations are present in the locale app with the Locale and LocaleHTML objects
    # However the privacy statement is not really a translation, but more a legal text.
    # We don't want translators to accidentally mess up these legal texts
    # and thus these text are stored with the PrivacyStatement model
    # Here we inject the privacy statement as a translation
    # in order for the frontend to simply switch between translations
    privacy_statement = PrivacyStatement.objects.get_latest_active()
    data["html-privacy-info"] = getattr(privacy_statement, locale)
    return Response(data)

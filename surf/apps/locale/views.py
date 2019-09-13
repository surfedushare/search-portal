from itertools import chain

from rest_framework.decorators import api_view
from rest_framework.response import Response

from surf.apps.locale.models import Locale, LocaleHTML


@api_view()
def get_localisation_strings(request, locale):
    translations = chain(Locale.objects.iterator(), LocaleHTML.objects.iterator())
    return Response({
        translation.translation_key: getattr(translation, locale, None)
        for translation in translations
    })

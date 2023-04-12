from django.apps import apps
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from surf.apps.core.search import get_search_client
from surf.apps.core.schema import SearchSchema
from surf.apps.materials.serializers import SimilaritySerializer, AuthorSuggestionSerializer
from surf.apps.materials.utils import add_extra_parameters_to_materials


filters_app = apps.get_app_config("filters")


class SimilarityAPIView(RetrieveAPIView):
    """
    This endpoint returns similar documents as the input document.
    These similar documents can be offered as suggestions to look at for the user.
    """

    serializer_class = SimilaritySerializer
    permission_classes = (AllowAny,)
    schema = SearchSchema()
    pagination_class = None
    filter_backends = []

    def get_object(self):
        serializer = self.get_serializer(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        external_id = serializer.validated_data["external_id"]
        language = serializer.validated_data["language"]
        client = get_search_client()
        result = client.more_like_this(external_id, language)
        result["results"] = add_extra_parameters_to_materials(filters_app.metadata, result["results"])
        return result


class AuthorSuggestionsAPIView(RetrieveAPIView):
    """
    This endpoint returns documents where the name of the author appears in the text or metadata,
    but is not set as author in the authors field.
    These documents can be offered to authors as suggestions for more content from their hand.
    """

    serializer_class = AuthorSuggestionSerializer
    permission_classes = (AllowAny,)
    schema = SearchSchema()
    pagination_class = None
    filter_backends = []

    def get_object(self):
        serializer = self.get_serializer(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        author_name = serializer.validated_data["author_name"]
        client = get_search_client()
        result = client.author_suggestions(author_name)
        result["results"] = add_extra_parameters_to_materials(filters_app.metadata, result["results"])
        return result

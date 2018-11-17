from django.db.models import Q, Count

from rest_framework.viewsets import (
    ModelViewSet,
    GenericViewSet
)

from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import action

from surf.apps.filters.models import FilterCategory
from surf.apps.filters.utils import IGNORED_FIELDS
from surf.apps.core.mixins import ListDestroyModelMixin

from surf.apps.materials.models import (
    Collection,
    Material,
    ApplaudMaterial,
    ViewMaterial
)

from surf.apps.materials.serializers import (
    SearchRequestSerializer,
    KeywordsRequestSerializer,
    MaterialsRequestSerializer,
    CollectionSerializer,
    CollectionMaterialsRequestSerializer,
    MaterialShortSerializer,
    ApplaudMaterialSerializer
)

from surf.apps.materials.filters import (
    ApplaudMaterialFilter,
    CollectionFilter
)

from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    XmlEndpointApiClient,
    AUTHOR_FIELD_ID,
    DISCIPLINE_FIELD_ID,
    CUSTOM_THEME_FIELD_ID,
    PUBLISHER_DATE_FILED_ID
)


class MaterialSearchAPIView(APIView):
    """
    View class that provides search action for Material by filters, author
    lookup text.
    """

    permission_classes = []

    def post(self, request, *args, **kwargs):
        # validate request parameters
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        # add additional filter by Author
        # if input data contains `author` parameter
        author = data.pop("author", None)
        if author:
            filters = data.get("filters", [])
            filters.append(dict(external_id=AUTHOR_FIELD_ID, items=[author]))
            data["filters"] = filters

        return_records = data.pop("return_records", None)
        return_filters = data.pop("return_filters", None)

        if not return_records:
            data["page_size"] = 0

        if return_filters:
            data["drilldown_names"] = _get_filter_categories()

        ac = XmlEndpointApiClient()
        res = ac.search(**data)

        records = _add_extra_parameters_to_materials(request.user,
                                                     res["records"])

        rv = dict(records=records,
                  records_total=res["recordcount"],
                  filters=res["drilldowns"],
                  page=data["page"],
                  page_size=data["page_size"])
        return Response(rv)


def _get_filter_categories():
    """
    Make list of filter categories in format "edurep_field_id:item_count"
    :return: list of "edurep_field_id:item_count"
    """
    return ["{}:{}".format(f.edurep_field_id, f.max_item_count)
            for f in FilterCategory.objects.all()
            if f.edurep_field_id not in IGNORED_FIELDS]


class KeywordsAPIView(APIView):
    """
    View class that provides search of keywords by text.
    """

    permission_classes = []

    def get(self, request, *args, **kwargs):
        # validate request parameters
        serializer = KeywordsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        ac = XmlEndpointApiClient()
        res = ac.autocomplete(**data)
        return Response(res)


class MaterialAPIView(APIView):
    """
    View class that provides retrieving Material by its edurep id (external_id)
    or retrieving overview of materials.
    If external_id is exist in request data then `get()` method returns
    material by external_id, otherwise it returns overview of materials.
    """

    permission_classes = []

    def get(self, request, *args, **kwargs):
        # validate request parameters
        serializer = MaterialsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        if "external_id" in data:
            # return Material by its edured id
            res = _get_material_details_by_id(data["external_id"])
            res = _add_extra_parameters_to_materials(request.user, res)
            ViewMaterial.add_unique_view(request.user, data["external_id"])

        else:
            # return overview of Materials
            ac = XmlEndpointApiClient()
            res = ac.search([],
                            ordering="-{}".format(PUBLISHER_DATE_FILED_ID),
                            page_size=4)

            res = _add_extra_parameters_to_materials(request.user,
                                                     res["records"])
        return Response(res)


_DISCIPLINE_FILTER = "{}:0".format(DISCIPLINE_FIELD_ID)


def _get_material_details_by_id(material_id):
    """
    Request from EduRep and return details of material by its EduRep id
    :param material_id: id of material in EduRep
    :return: list of requested materials
    """
    ac = XmlEndpointApiClient()
    res = ac.get_materials_by_id(['"{}"'.format(material_id)],
                                 drilldown_names=[_DISCIPLINE_FILTER])

    # define themes and disciplines for requested material
    themes = []
    disciplines = []
    for f in res.get("drilldowns", []):
        if f["external_id"] == CUSTOM_THEME_FIELD_ID:
            themes = [item["external_id"] for item in f["items"]]
        elif f["external_id"] == DISCIPLINE_FIELD_ID:
            disciplines = [item["external_id"] for item in f["items"]]

    # set extra details for requested material
    rv = res.get("records", [])
    for material in rv:
        material["themes"] = themes
        material["disciplines"] = disciplines

        m = Material.objects.filter(external_id=material_id).first()
        if m:
            material["number_of_collections"] = m.collections.count()

    return rv


class CollectionViewSet(ModelViewSet):
    """
    View class that provides CRUD methods for Collection and `get`, `add`
    and `delete` methods for its materials.
    """

    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    filter_class = CollectionFilter
    permission_classes = []

    def get_queryset(self):
        qs = Collection.objects.annotate(community_cnt=Count('communities'))

        # shared collections
        filters = Q(is_shared=True)

        # add own collections
        user = self.request.user
        if user and user.is_active:
            filters |= Q(owner_id=user.id)

        # add collections in communities
        filters |= Q(community_cnt__gt=0)

        return qs.filter(filters)

    def create(self, request, *args, **kwargs):
        # only active and authorized users can create collection
        self._check_access(request.user)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # only active owners can update collection
        self._check_access(request.user, instance=self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # only active owners can delete collection
        self._check_access(request.user, instance=self.get_object())
        return super().destroy(request, *args, **kwargs)

    @action(methods=['get', 'post', 'delete'], detail=True)
    def materials(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if request.method == "GET":
            # validate request parameters
            serializer = CollectionMaterialsRequestSerializer(data=request.GET)
            serializer.is_valid(raise_exception=True)
            data = dict(serializer.validated_data)

            ids = ['"{}"'.format(m.external_id)
                   for m in instance.materials.order_by("id").all()]

            res = []
            if ids:
                ac = XmlEndpointApiClient()
                res = ac.get_materials_by_id(ids, **data)
                res = res.get("records", [])
                res = _add_extra_parameters_to_materials(request.user, res)
            return Response(res)

        # only owners can add/delete materials to/from collection
        self._check_access(request.user, instance=instance)
        data = []
        for d in request.data:
            # validate request parameters
            serializer = MaterialShortSerializer(data=d)
            serializer.is_valid(raise_exception=True)
            data.append(dict(serializer.validated_data))

        if request.method == "POST":
            self._add_materials(instance, data)

        elif request.method == "DELETE":
            self._delete_materials(instance, data)

        return Response([m.external_id for m in instance.materials.all()])

    @staticmethod
    def _add_materials(instance, materials):
        """
        Add materials to collection
        :param instance: collection instance
        :param materials: added materials
        :return:
        """
        for material in materials:
            m_external_id = material["external_id"]
            m, _ = Material.objects.get_or_create(
                external_id=m_external_id,
                defaults=dict(external_id=m_external_id))
            instance.materials.add(m)

    @staticmethod
    def _delete_materials(instance, materials):
        """
        Delete materials from collection
        :param instance: collection instance
        :param materials: deleted materials
        :return:
        """
        for material in materials:
            m_external_id = material["external_id"]
            try:
                m = Material.objects.get(external_id=m_external_id)
                instance.materials.remove(m)
            except Material.DoesNotExist:
                pass

    @staticmethod
    def _check_access(user, instance=None):
        """
        Check if user is active and owner of collection (if collection
        is not None)
        :param user: user
        :param instance: collection instance
        :return:
        """
        if not user or not user.is_active:
            raise AuthenticationFailed()

        if instance and (instance.owner_id != user.id):
            raise AuthenticationFailed()


class ApplaudMaterialViewSet(ListModelMixin,
                             CreateModelMixin,
                             ListDestroyModelMixin,
                             GenericViewSet):
    """
    View class that provides `get`, `create` and `delete` methods
    for Applaud Material.
    """

    queryset = ApplaudMaterial.objects.all()
    serializer_class = ApplaudMaterialSerializer
    permission_classes = [IsAuthenticated]
    filter_class = ApplaudMaterialFilter

    def get_queryset(self):
        # filter only "applauds" of current user
        qs = super().get_queryset()
        qs = qs.filter(user_id=self.request.user.id)
        return qs


def _add_extra_parameters_to_materials(user, materials):
    """
    Add additional parameters for materials (bookmark, number of applauds,
    number of views)
    :param user: user who requested material
    :param materials: array of materials
    :return: updated array of materials
    """
    for m in materials:
        if user and user.id:
            qs = Material.objects.prefetch_related("collections")
            qs = qs.filter(collections__owner_id=user.id,
                           external_id=m["external_id"])
            m["has_bookmark"] = qs.exists()

        qs = ApplaudMaterial.objects.prefetch_related("material")
        qs = qs.filter(material__external_id=m["external_id"])
        m["number_of_applauds"] = qs.count()

        qs = ViewMaterial.objects.prefetch_related("material")
        qs = qs.filter(material__external_id=m["external_id"])
        m["number_of_views"] = qs.count()

    return materials

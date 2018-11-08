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
    ApplaudMaterial
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

from surf.apps.materials.filters import ApplaudMaterialFilter

from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    XmlEndpointApiClient,
    AUTHOR_FIELD_ID,
    PUBLISHER_FIELD_ID,
    DISCIPLINE_FIELD_ID,
    CUSTOM_THEME_FIELD_ID
)


class MaterialSearchAPIView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        author = data.pop("author", None)
        if author:
            filters = data.get("filters", [])
            filters.append(dict(external_id=AUTHOR_FIELD_ID, items=[author]))
            # filters.append(dict(external_id=PUBLISHER_FIELD_ID,
            #                     items=[author]))
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
    return ["{}:{}".format(f.edurep_field_id, f.max_item_count)
            for f in FilterCategory.objects.all()
            if f.edurep_field_id not in IGNORED_FIELDS]


class KeywordsAPIView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        serializer = KeywordsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        ac = XmlEndpointApiClient()
        res = ac.autocomplete(**data)
        return Response(res)


class MaterialAPIView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        serializer = MaterialsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)

        if "external_id" in data:
            res = _get_material_details_by_id(data["external_id"])
            res = _add_extra_parameters_to_materials(request.user, res)
        else:
            # TODO to be implemented
            res = []
        return Response(res)


_DISCIPLINE_FILTER = "{}:0".format(DISCIPLINE_FIELD_ID)


def _get_material_details_by_id(material_id):
    ac = XmlEndpointApiClient()
    res = ac.get_materials_by_id(['"{}"'.format(material_id)],
                                 drilldown_names=[_DISCIPLINE_FILTER])

    themes = []
    for f in res.get("drilldowns", []):
        if f["external_id"] == CUSTOM_THEME_FIELD_ID:
            themes = [item["external_id"] for item in f["items"]]

    rv = res.get("records", [])
    for material in rv:
        material["themes"] = themes

    return rv


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        self._check_access(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._check_access(request, instance=self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._check_access(request, instance=self.get_object())
        return super().destroy(request, *args, **kwargs)

    @action(methods=['get', 'post', 'delete'], detail=True)
    def materials(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if request.method == "GET":
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

        self._check_access(request, instance=instance)
        data = []
        for d in request.data:
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
        for material in materials:
            m_external_id = material["external_id"]
            m, _ = Material.objects.get_or_create(
                external_id=m_external_id,
                defaults=dict(external_id=m_external_id))
            instance.materials.add(m)

    @staticmethod
    def _delete_materials(instance, materials):
        for material in materials:
            m_external_id = material["external_id"]
            try:
                m = Material.objects.get(external_id=m_external_id)
                instance.materials.remove(m)
            except Material.DoesNotExist:
                pass

    @staticmethod
    def _check_access(request, instance=None):
        user = request.user
        if not user or not user.is_active:
            raise AuthenticationFailed()

        if instance and (instance.owner_id != user.id):
            raise AuthenticationFailed()


class ApplaudMaterialViewSet(ListModelMixin,
                             CreateModelMixin,
                             ListDestroyModelMixin,
                             GenericViewSet):
    queryset = ApplaudMaterial.objects.all()
    serializer_class = ApplaudMaterialSerializer
    permission_classes = [IsAuthenticated]
    filter_class = ApplaudMaterialFilter

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user_id=self.request.user.id)
        return qs


def _add_extra_parameters_to_materials(user, materials):
    if not user or not user.id:
        return materials

    for m in materials:
        qs = Material.objects.prefetch_related("collections")
        qs = qs.filter(collections__owner_id=user.id,
                       external_id=m["external_id"])
        m["has_bookmark"] = qs.exists()
    return materials

from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response

from surf.apps.materials.models import Material


class MaterialRatingAPIView(APIView):

    def post(self, request, *args, **kwargs):
        params = request.data.get('params')
        external_id = params['external_id']
        star_rating = params['star_rating']
        material_object = Material.objects.get(external_id=external_id, deleted_at=None)
        if star_rating == 1:
            material_object.star_1 = F('star_1') + 1
        if star_rating == 2:
            material_object.star_2 = F('star_2') + 1
        if star_rating == 3:
            material_object.star_3 = F('star_3') + 1
        if star_rating == 4:
            material_object.star_4 = F('star_4') + 1
        if star_rating == 5:
            material_object.star_5 = F('star_5') + 1
        material_object.save()
        material_object.refresh_from_db()
        return Response(material_object.get_avg_star_rating())


class MaterialApplaudAPIView(APIView):

    def post(self, request, *args, **kwargs):
        params = request.data.get('params')
        external_id = params['external_id']
        material_object = Material.objects.get(external_id=external_id, deleted_at=None)
        material_object.applaud_count = F('applaud_count') + 1
        material_object.save()
        material_object.refresh_from_db()
        return Response(material_object.applaud_count)

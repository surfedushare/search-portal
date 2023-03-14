from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, schema, permission_classes
from rest_framework.permissions import AllowAny


class ConfigAPIView(APIView):
    """
    View class that provides detail information about current user .
    """

    @api_view()
    @permission_classes([AllowAny])
    @schema(None)
    def config(request):
        print(settings)
        data = {"use_api_endpoint": settings.USE_API_ENDPOINT}
        return Response(data, status.HTTP_200_OK)


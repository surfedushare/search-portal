from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, schema, permission_classes
from rest_framework.permissions import AllowAny

from packaging import get_package_info


@api_view()
@permission_classes([AllowAny])
@schema(None)
def health_check(request):
    data = {"healthy" : True}
    package_info = get_package_info()
    data.update(package_info)
    return Response(data, status.HTTP_200_OK)

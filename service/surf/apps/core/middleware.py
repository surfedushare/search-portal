import ipaddress

from django.conf import settings
from django.urls import resolve
from django.core.exceptions import PermissionDenied


def get_request_ips(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ips = x_forwarded_for.split(',')
        ips = map(str.strip, ips)
    else:
        ips = [request.META.get('REMOTE_ADDR')]

    return ips


def has_allowed_ip(request):
    ips = get_request_ips(request)
    for request_ip_str in ips:
        request_ip = ipaddress.ip_address(request_ip_str)

        for allowed_range in settings.ADMIN_IP_WHITELIST:
            network = ipaddress.ip_network(allowed_range)
            if request_ip in network:
                return True

    return False


class RestrictAdminAccess:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        app_name = resolve(request.path).app_name

        if app_name == 'admin':
            if has_allowed_ip(request) is False:
                raise PermissionDenied()

        return self.get_response(request)

from rest_framework.permissions import BasePermission


class IsActive(BasePermission):
    """
    Allows access only to active users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active

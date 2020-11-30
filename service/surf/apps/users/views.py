import logging
from sentry_sdk import capture_message

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.cache import never_cache
from django.contrib.sessions.models import Session

from surf.vendor.surfconext.models import PrivacyStatement, DataGoalPermissionSerializer
from surf.apps.users.models import SessionToken
from surf.apps.users.serializers import UserDetailsSerializer


logger = logging.getLogger(__name__)


class UserDetailsAPIView(APIView):
    """
    View class that provides detail information about current user .
    """

    @never_cache
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            data = UserDetailsSerializer().to_representation(request.user)
        else:
            data = {}
        privacy_statement = PrivacyStatement.objects.get_latest_active()
        if privacy_statement is None:
            capture_message("Trying to retrieve user details without an active privacy statement")
        permissions = request.session.get("permissions", None)
        if privacy_statement:
            permissions = request.session["permissions"] = \
                privacy_statement.get_privacy_settings(request.user, permissions)
        data["permissions"] = permissions
        request.session.modified = True  # this extends expiry
        return Response(data)

    @never_cache
    def post(self, request, *args, **kwargs):
        # Handle the permissions part of the data
        raw_permission = request.data.get("permissions", None)
        serializer = DataGoalPermissionSerializer(data=raw_permission, many=True, context={"user": request.user})
        serializer.is_valid(raise_exception=True)
        permissions = []
        for permission_data in serializer.validated_data:
            permission = dict(permission_data)
            goal = permission.pop("goal")
            permission.update(**goal)
            permissions.append(permission)

        # Either write these permissions to the user or to the session
        if request.user.is_authenticated:
            for permission in permissions:
                serializer.create(permission)
            # Notice that we clear the permissions from session to allow re-creation (in GET method)
            if "permissions" in request.session:
                del request.session["permissions"]
        else:
            request.session["permissions"] = permissions

        return self.get(request, *args, **kwargs)


class ObtainTokenAPIView(APIView):

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    @never_cache
    def get(self, request, *args, **kwargs):
        token, created = SessionToken.objects.get_or_create(user=request.user)
        session_key = request.session.session_key
        if not token.sessions.filter(session_key=session_key).exists():
            session = Session.objects.get(session_key=session_key)
            token.sessions.add(session)
        # Now that we're starting a session with this token
        # We need to reload permission settings into the session for the user from the database
        # Deleting the current session permissions will force a reload when accessing those settings next time
        if "permissions" in request.session:
            del request.session["permissions"]
        return Response({'token': token.key})

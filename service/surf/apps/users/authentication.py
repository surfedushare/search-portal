from django.contrib.auth.signals import user_logged_out
from rest_framework.authentication import TokenAuthentication

from surf.apps.users.models import SessionToken


class SessionTokenAuthentication(TokenAuthentication):
    model = SessionToken


def delete_api_auth_token(sender, user, request, **kwargs):
    try:
        if user is not None:
            user.auth_token.delete()
    except SessionToken.DoesNotExist:
        pass


user_logged_out.connect(delete_api_auth_token)

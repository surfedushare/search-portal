from rest_framework.authentication import TokenAuthentication

from surf.apps.users.models import SessionToken


class SessionTokenAuthentication(TokenAuthentication):
    model = SessionToken

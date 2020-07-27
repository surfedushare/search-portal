from django.conf import settings

from social_core.backends.open_id_connect import OpenIdConnectAuth


class SurfConextOpenIDConnectBackend(OpenIdConnectAuth):

    name = "surf-conext"
    OIDC_ENDPOINT = settings.SOCIAL_AUTH_SURF_CONEXT_OIDC_ENDPOINT
    DEFAULT_SCOPE = ["openid", "groups"]

    def get_jwks_keys(self):
        return self.get_remote_jwks_keys()

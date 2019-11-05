from social_core.backends.open_id_connect import OpenIdConnectAuth


class SurfConextOpenIDConnectBackend(OpenIdConnectAuth):

    name = "surf-conext"
    OIDC_ENDPOINT = "https://oidc.test.surfconext.nl"
    DEFAULT_SCOPE = ["openid", "groups"]
